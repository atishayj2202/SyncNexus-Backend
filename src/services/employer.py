from uuid import UUID

from fastapi import HTTPException, status

from src.client.cockroach import CockroachDBClient
from src.db.tables.employee_location import EmployeeLocation
from src.db.tables.employee_mapping import EmployeeMapping
from src.db.tables.job import Jobs
from src.db.tables.payment import Payment
from src.db.tables.task import Task
from src.db.tables.user import User
from src.responses.employee import EmployeeResponse
from src.responses.job import JobCreateRequest
from src.responses.task import TaskCreateRequest
from src.responses.user import PaymentRequest, PaymentResponse, UserResponse
from src.responses.util import DurationRequest, Location


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
        cls, employee_id: UUID, cockroach_client: CockroachDBClient, user: User
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
                    done=None,
                    amount=request.amount,
                    deleted=None,
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
        for i in employees:
            if i.deleted is not None:
                temp[i.employee_id] = i.status
            else:
                temp[i.employee_id] = i.status
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
                    status=temp[user.id],
                )
            )
        return employee_response

    @classmethod
    def search_employee(
        cls, cockroach_client: CockroachDBClient, phone_no: str
    ) -> UserResponse:
        user = cockroach_client.query(
            User.get_by_field_unique,
            field="phone_no",
            match_value=phone_no,
            error_not_exist=False,
        )
        if user is None:
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
        cls, user: User, request: PaymentRequest, cockroach_client: CockroachDBClient
    ) -> None:
        cockroach_client.query(
            Payment.add,
            items=[
                Payment(
                    amount=request.amount,
                    from_user_id=user.id,
                    to_user_id=request.to_user_id,
                    currency=request.currency,
                    remarks=request.remarks,
                )
            ],
        )

    @classmethod
    def fetch_employee_payments(
        cls, cockroach_client: CockroachDBClient, user: User, user_id: UUID
    ) -> list[PaymentResponse]:
        payments: list[Payment] | None = cockroach_client.query(
            Payment.get_by_multiple_field_unique,
            fields=["from_user_id", "to_user_id"],
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
                from_user_id=payment.from_user_id,
                to_user_id=payment.to_user_id,
                currency=payment.currency,
                remarks=payment.remarks,
                approved_at=payment.approved_at,
            )
            for payment in payments
        ]
