from uuid import UUID

from fastapi import HTTPException
from starlette import status

from src.client.cockroach import CockroachDBClient
from src.db.tables.employee_location import EmployeeLocation
from src.db.tables.employee_mapping import EmployeeMapping
from src.db.tables.job import Jobs
from src.db.tables.payment import Payment
from src.db.tables.task import Task
from src.db.tables.user import User
from src.responses.employee import EmployeeResponse
from src.responses.job import JobResponse
from src.responses.task import TaskResponse
from src.responses.user import UserResponse
from src.responses.util import DurationRequest, Location
from src.utils.enums import EmployeeStatus, TaskStatus
from src.utils.time import get_current_time


class EmployeeService:
    @classmethod
    def fetch_task(cls, task: Task) -> TaskResponse:
        temp = TaskStatus.pending
        if task.completed is not None:
            temp = TaskStatus.completed
        elif task.deleted is not None:
            temp = TaskStatus.cancelled
        return TaskResponse(
            id=task.id,
            created_at=task.created_at,
            employee_id=task.employee_id,
            employer_id=task.employer_id,
            heading=task.heading,
            description=task.description,
            last_date=task.last_date,
            status=temp,
        )

    @classmethod
    def fetch_tasks(
        cls,
        employee: User,
        cockroach_client: CockroachDBClient,
        request: DurationRequest,
    ) -> list[TaskResponse]:
        tasks: list[Task] | None = cockroach_client.query(
            Task.get_by_time_field_multiple,
            time_field="created_at",
            start_time=request.start_time,
            end_time=request.end_time,
            field="employee_id",
            match_value=employee.id,
            error_not_exist=False,
        )
        response_list = []
        if tasks is None:
            return response_list
        for task in tasks:
            response_list.append(cls.fetch_task(task))
        return response_list

    @classmethod
    def fetch_job(
        cls,
        cockroach_client: CockroachDBClient,
        job_id: UUID,
    ):
        job = cockroach_client.query(Jobs.get_id, id=job_id, error_not_exist=False)
        if job is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job Not Found",
            )
        return cls.fetch_job_detail(job)

    @classmethod
    def add_location(
        cls,
        location: Location,
        user: User,
        cockroach_client: CockroachDBClient,
    ) -> None:
        cockroach_client.query(
            EmployeeLocation.add,
            items=[
                EmployeeLocation(
                    employee_id=user.id,
                    location_lat=location.location_lat,
                    location_long=location.location_long,
                )
            ],
        )

    @classmethod
    def leave_job(cls, cockroach_client: CockroachDBClient, user: User):
        employee_mapping = cockroach_client.query(
            EmployeeMapping.get_by_multiple_field_unique,
            fields=["employee_id", "deleted"],
            match_values=[user.id, None],
            error_not_exist=False,
        )
        if employee_mapping is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Not Employed",
            )
        employee_mapping.deleted = get_current_time()
        employee_mapping.status = EmployeeStatus.left
        cockroach_client.query(
            EmployeeMapping.update_by_id,
            id=employee_mapping.id,
            new_data=employee_mapping,
        )

    @classmethod
    def fetch_job_detail(cls, job: Jobs) -> JobResponse:
        return JobResponse(
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

    @classmethod
    def complete_task(
        cls,
        task: Task,
        cockroach_client: CockroachDBClient,
    ) -> None:
        if task.completed is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Task Already Completed",
            )
        if task.deleted is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Task Already Deleted",
            )
        task.completed = get_current_time()
        cockroach_client.query(
            Task.update_by_id,
            id=task.id,
            new_data=task,
        )

    @classmethod
    def get_jobs(
        cls, cockroach_client: CockroachDBClient, request: Location
    ) -> list[JobResponse]:
        jobs: list[Jobs] | None = cockroach_client.query(
            Jobs.get_multiple_in_radius,
            radius=25000,
            lat=request.location_lat,
            lon=request.location_long,
            error_not_exist=False,
        )
        if jobs is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Jobs Found",
            )
        return [cls.fetch_job_detail(job=job) for job in jobs]

    @classmethod
    def approve_payment(
        cls,
        payment_id: UUID,
        user: User,
        cockroach_client: CockroachDBClient,
    ) -> None:
        payment: Payment = cockroach_client.query(
            Payment.get_id,
            id=payment_id,
            error_not_exist=False,
        )
        if payment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment Not Found",
            )
        if payment.to_user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Payment Not for User",
            )
        if payment.approved_at is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Payment Already Approved",
            )
        payment.approved_at = get_current_time()
        cockroach_client.query(
            Payment.update_by_id,
            id=payment.id,
            new_data=payment,
        )

    @classmethod
    def fetch_employer(
        cls, cockroach_client: CockroachDBClient, user: User
    ) -> UserResponse:
        employee_mapping: EmployeeMapping = cockroach_client.query(
            EmployeeMapping.get_by_multiple_field_unique,
            fields=["employee_id", "deleted"],
            match_values=[user.id, None],
            error_not_exist=False,
        )
        if employee_mapping is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Not Employed",
            )
        employer: User = cockroach_client.query(
            User.get_id,
            id=employee_mapping.employer_id,
            error_not_exist=False,
        )
        if employer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employer Not Found",
            )
        return UserResponse(
            id=employer.id,
            name=employer.name,
            phone_no=employer.phone_no,
            email=employer.email,
            created_at=employer.created_at,
            user_type=employer.user_type,
        )

    @classmethod
    def fetch_employee_job(
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
                status_code=status.HTTP_409_CONFLICT,
                detail="Not Employed",
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
