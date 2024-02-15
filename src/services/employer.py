from uuid import UUID

from fastapi import HTTPException, status

from src.client.cockroach import CockroachDBClient
from src.db.tables.employee_location import EmployeeLocation
from src.db.tables.employee_mapping import EmployeeMapping
from src.db.tables.job import Jobs
from src.db.tables.payment import Payment
from src.db.tables.task import Task
from src.db.tables.user import User
from src.db.views.payment import PaymentDetails
from src.responses.employee import EmployeeResponse
from src.responses.job import JobCreateRequest, JobResponse
from src.responses.task import TaskCreateRequest
from src.responses.user import PaymentRequest, PaymentResponse, UserResponse
from src.responses.util import DurationRequest, Location
from src.utils.enums import EmployeeStatus, UserType
from src.utils.time import get_current_time


class EmployerService:
    @classmethod
    def __verify_employee(
        cls,
        employee_id: UUID,
        employer: User,
        cockroach_client: CockroachDBClient,
        is_employer: bool = True,
    ) -> None:
        employee = cockroach_client.query(
            User.get_id, id=employee_id, error_not_exist=False
        )
        if employee is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Employee not Found"
            )
        employee_mapping = cockroach_client.query(
            EmployeeMapping.get_by_multiple_field_unique,
            fields=["employee_id", "employer_id", "deleted"],
            match_values=[employee_id, employer.id, None],
            error_not_exist=False,
        )
        if employee_mapping is None and is_employer:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Employee not Under Employer",
            )
        if employee_mapping is not None and not is_employer:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Employee is already Employed",
            )

    @classmethod
    def add_task(
        cls, request: TaskCreateRequest, cockroach_client: CockroachDBClient, user: User
    ) -> None:
        cls.__verify_employee(
            request.employee_id, user, cockroach_client, is_employer=True
        )
        cockroach_client.query(
            Task.add,
            items=[
                Task(
                    employee_id=request.employee_id,
                    employer_id=user.id,
                    heading=request.heading,
                    description=request.description,
                    last_date=request.last_date,
                    deleted=None,
                    completed=None,
                )
            ],
        )

    @classmethod
    def add_employee(
        cls,
        employee_id: UUID,
        cockroach_client: CockroachDBClient,
        user: User,
        title: str,
    ) -> None:
        cls.__verify_employee(employee_id, user, cockroach_client, is_employer=False)
        employee_mapping = cockroach_client.query(
            EmployeeMapping.get_by_multiple_field_unique,
            fields=["employee_id", "deleted"],
            match_values=[employee_id, None],
            error_not_exist=False,
        )
        if employee_mapping is not None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Employee is Employed",
            )
        cockroach_client.query(
            EmployeeMapping.add,
            items=[
                EmployeeMapping(
                    employee_id=employee_id,
                    employer_id=user.id,
                    title=title,
                )
            ],
        )

    @classmethod
    def add_job(
        cls, request: JobCreateRequest, cockroach_client: CockroachDBClient, user: User
    ) -> None:
        cockroach_client.query(
            Jobs.add,
            items=[
                Jobs(
                    employer_id=user.id,
                    title=request.title,
                    description=request.description,
                    location_lat=request.location_lat,
                    location_long=request.location_long,
                    amount=request.amount,
                )
            ],
        )

    @classmethod
    def fetch_employees(
        cls, cockroach_client: CockroachDBClient, user: User
    ) -> list[EmployeeResponse]:
        employees: list[EmployeeMapping] = cockroach_client.query(
            EmployeeMapping.get_by_field_multiple,
            field="employer_id",
            match_value=user.id,
            error_not_exist=False,
        )
        temp = {}
        if employees is None:
            return []
        for i in employees:
            if (
                temp.get(i.employee_id) is None
                or i.deleted is None
                or (
                    temp.get(i.employee_id) is not None
                    and temp[i.employee_id][2] < i.deleted
                )
            ):
                temp[i.employee_id] = [i.status, i.title, i.deleted, i.created_at]
        users: list[User] = cockroach_client.query(
            User.get_by_field_value_list,
            field="id",
            match_values=temp.keys(),
            error_not_exist=False,
        )
        employee_response = []
        if users is None:
            return employee_response
        for user in users:
            employee_response.append(
                EmployeeResponse(
                    employee_id=user.id,
                    name=user.name,
                    phone_no=user.phone_no,
                    title=temp[user.id][1],
                    status=temp[user.id][0],
                    join_date=temp[user.id][3],
                    email=user.email,
                )
            )
        return employee_response

    @classmethod
    def fetch_employee(
        cls, cockroach_client: CockroachDBClient, user: User
    ) -> EmployeeResponse:
        employee_mapping: EmployeeMapping = cockroach_client.query(
            EmployeeMapping.get_by_multiple_field_unique,
            fields=["employee_id", "deleted"],
            match_values=[user.id, None],
            error_not_exist=False,
        )
        if employee_mapping is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No Employee Found"
            )
        return EmployeeResponse(
            employee_id=user.id,
            name=user.name,
            phone_no=user.phone_no,
            title=employee_mapping.title,
            status=employee_mapping.status,
            join_date=employee_mapping.created_at,
            email=user.email,
        )

    @classmethod
    def search_employee_by_phone(
        cls, cockroach_client: CockroachDBClient, phone_no: str
    ) -> UserResponse:
        user: User = cockroach_client.query(
            User.get_by_field_unique,
            field="phone_no",
            match_value=phone_no,
            error_not_exist=False,
        )
        if user is None or user.user_type == UserType.employer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not Found"
            )
        employee_mapping = cockroach_client.query(
            EmployeeMapping.get_by_multiple_field_unique,
            fields=["employee_id", "deleted"],
            match_values=[user.id, None],
            error_not_exist=False,
        )
        if employee_mapping is not None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Employee is Employed",
            )
        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            phone_no=user.phone_no,
            user_type=user.user_type,
            created_at=user.created_at,
        )

    @classmethod
    def search_employee_by_email(
        cls, cockroach_client: CockroachDBClient, email: str
    ) -> UserResponse:
        user: User = cockroach_client.query(
            User.get_by_field_unique,
            field="email",
            match_value=email,
            error_not_exist=False,
        )
        if user is None or user.user_type == UserType.employer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not Found"
            )
        employee_mapping = cockroach_client.query(
            EmployeeMapping.get_by_multiple_field_unique,
            fields=["employee_id", "deleted"],
            match_values=[user.id, None],
            error_not_exist=False,
        )
        if employee_mapping is not None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Employee is Employed",
            )
        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            phone_no=user.phone_no,
            user_type=user.user_type,
            created_at=user.created_at,
        )

    @classmethod
    def fetch_location_path(
        cls, cockroach_client: CockroachDBClient, user: User, request: DurationRequest
    ) -> list[Location]:
        locations: list[EmployeeLocation] | None = cockroach_client.query(
            EmployeeLocation.get_by_time_field_multiple,
            time_field="created_at",
            start_time=request.start_time,
            end_time=request.end_time,
            field="employee_id",
            match_value=user.id,
            error_not_exist=False,
        )
        if locations is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No Location Found"
            )
        return [
            Location(
                location_lat=location.location_lat,
                location_long=location.location_long,
                created_at=location.created_at,
            )
            for location in locations
        ]

    @classmethod
    def add_payment(
        cls,
        user: User,
        request: PaymentRequest,
        cockroach_client: CockroachDBClient,
        employee_id: UUID,
    ) -> None:
        cockroach_client.query(
            Payment.add,
            items=[
                Payment(
                    amount=request.amount,
                    from_user_id=user.id,
                    to_user_id=employee_id,
                    currency=request.currency,
                    remarks=request.remarks,
                )
            ],
        )

    @classmethod
    def fetch_employee_payments(
        cls, cockroach_client: CockroachDBClient, user: User, user_id: UUID
    ) -> list[PaymentResponse]:
        payments: list[PaymentDetails] | None = cockroach_client.query(
            PaymentDetails.get_by_multiple_field_multiple,
            fields=["sender_id", "receiver_id"],
            match_values=[user.id, user_id],
            error_not_exist=False,
        )
        if payments is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No Payments Found"
            )
        return [
            PaymentResponse(
                id=payment.id,
                amount=payment.amount,
                created_at=payment.created_at,
                from_user=UserResponse(
                    id=payment.sender_id,
                    name=payment.sender_name,
                    phone_no=payment.sender_phone,
                    email=payment.sender_email,
                    user_type=payment.sender_user_type,
                ),
                to_user=UserResponse(
                    id=payment.receiver_id,
                    name=payment.receiver_name,
                    phone_no=payment.receiver_phone,
                    email=payment.receiver_email,
                    user_type=payment.receiver_user_type,
                ),
                currency=payment.currency,
                remarks=payment.remarks,
                approved_at=payment.approved_at,
            )
            for payment in payments
        ]

    @classmethod
    def remove_employee(
        cls,
        cockroach_client: CockroachDBClient,
        user_employee: User,
        user_employer: User,
    ):
        employee_mapping = cockroach_client.query(
            EmployeeMapping.get_by_multiple_field_unique,
            fields=["employee_id", "employer_id", "deleted"],
            match_values=[user_employee.id, user_employer.id, None],
            error_not_exist=False,
        )
        if employee_mapping is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Not Employed",
            )
        employee_mapping.deleted = get_current_time()
        employee_mapping.status = EmployeeStatus.removed
        cockroach_client.query(
            EmployeeMapping.update_by_id,
            id=employee_mapping.id,
            new_data=employee_mapping,
        )

    @classmethod
    def delete_job(cls, job_id: UUID, cockroach_client: CockroachDBClient, user: User):
        job: Jobs = cockroach_client.query(
            Jobs.get_by_multiple_field_unique,
            fields=["id", "employer_id", "deleted"],
            match_values=[job_id, user.id, None],
            error_not_exist=False,
        )
        if job is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not Found",
            )
        if job.done is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Job already completed",
            )
        job.deleted = get_current_time()
        cockroach_client.query(
            Jobs.update_by_id,
            id=job.id,
            new_data=job,
        )

    @classmethod
    def complete_job(
        cls, job_id: UUID, cockroach_client: CockroachDBClient, user: User
    ):
        job: Jobs = cockroach_client.query(
            Jobs.get_by_multiple_field_unique,
            fields=["id", "employer_id", "deleted"],
            match_values=[job_id, user.id, None],
            error_not_exist=False,
        )
        if job is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not Found",
            )
        if job.done is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Job already completed",
            )
        job.done = get_current_time()
        cockroach_client.query(
            Jobs.update_by_id,
            id=job.id,
            new_data=job,
        )

    @classmethod
    def delete_task(cls, user: User, cockroach_client: CockroachDBClient, task: Task):
        if user.id != task.employer_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized",
            )
        if task.deleted is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Task already deleted",
            )
        if task.completed is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Task already completed",
            )
        task.deleted = get_current_time()
        cockroach_client.query(
            Task.update_by_id,
            id=task.id,
            new_data=task,
        )

    @classmethod
    def get_jobs(
        cls, cockroach_client: CockroachDBClient, user: User
    ) -> list[JobResponse]:
        jobs: list[Jobs] = cockroach_client.query(
            Jobs.get_by_field_multiple,
            field="employer_id",
            match_value=user.id,
            error_not_exist=False,
        )
        if jobs is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Jobs Found",
            )
        return [
            JobResponse(
                id=job.id,
                created_at=job.created_at,
                employer_id=job.employer_id,
                title=job.title,
                description=job.description,
                location=Location(
                    location_lat=job.location_lat, location_long=job.location_long
                ),
                done=job.done,
                amount=job.amount,
                deleted=job.deleted,
            )
            for job in jobs
        ]
