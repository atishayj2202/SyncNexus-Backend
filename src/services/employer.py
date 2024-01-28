from uuid import UUID

from fastapi import HTTPException, status

from src.client.cockroach import CockroachDBClient
from src.db.employee_mapping import Employee_Mapping
from src.db.employee_location import EmployeeLocation
from src.db.job import Jobs
from src.db.task import Task
from src.db.user import User
from src.responses.employee import EmployeeCreateRequest
from src.responses.job import JobCreateRequest
from src.responses.task import TaskCreateRequest


class EmployerService:
    @classmethod
    def __verify_employee(
        cls, employee_id: UUID, employer: User, cockroach_client: CockroachDBClient
    ) -> None:
        employee = cockroach_client.query(
            User.get_id, id=employee_id, error_not_exist=False
        )
        if employee is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Employee not Found"
            )
        employee_mapping = cockroach_client.query(
            Employee_Mapping.get_by_multiple_field_unique,
            fields=["employee_id", "employer_id", "deleted"],
            match_values=[employee_id, employer.id, None],
            error_not_exist=False,
        )
        if employee_mapping is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Employee not Under Employer",
            )

        if employee_mapping is not None:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Employee is already Employed",
            )

    @classmethod
    def add_task(
        cls, request: TaskCreateRequest, cockroach_client: CockroachDBClient, user: User
    ) -> None:
        cls.__verify_employee(request.employee_id, user, cockroach_client)
        cockroach_client.query(
            Task.add,
            items=[
                Task(
                    employee_id=request.employee_id,
                    employer_id=request.employer_id,
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
        cls, request: EmployeeCreateRequest, cockroach_client: CockroachDBClient
    ) -> None:
        employee_mapping = cockroach_client.query(
            Employee_Mapping.get_by_multiple_field_unique,
            fields=["employee_id", "deleted"],
            match_values=[request.employee_id, None],
            error_not_exist=False,
        )
        if employee_mapping is not None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Employee is Employed",
            )
        cockroach_client.query(
            Employee_Mapping.add,
            items=[
                Employee_Mapping(
                    employee_id=request.employee_id,
                    employer_id=request.employer_id,
                )
            ],
        )

    @classmethod
    def add_job(
        cls, request: JobCreateRequest, cockroach_client: CockroachDBClient
    ) -> None:
        cockroach_client.query(
            Jobs.add,
            items=[
                Jobs(
                    employer_id=request.employer_id,
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

    """@classmethod
    def fetch_employee(
            cls, cockroach_client: CockroachDBClient
    ) -> None:
        employee = cockroach_client.query(
            employee_mapping=cockroach_client.query(
                Employee_Mapping.get_by_multiple_field_unique,
                fields=["employee_id", "employer_id", "deleted"],
                match_values=[employee_id, employer.id, None],
                error_not_exist=False,
            )
        )"""


    @classmethod
    def fetch_employees(
            cls, cockroach_client: CockroachDBClient
    ) -> None:
        employees: List[Employee_Mapping] = cockroach_client.query(
            employee_mapping=cockroach_client.query(
                Employee_Mapping.get_by_multiple_field_unique,
                fields=["employee_id", "employer_id", "deleted"],
                match_values=[employee_id, employer.id, None],
                error_not_exist=False,
            )
        )


    @classmethod
    def fetch_employee_location(
            cls, cockroach_client: CockroachDBClient
    ) -> None:
        employee_location = cockroach_client.query(
            employee_mapping=cockroach_client.query(
                EmployeeLocation.get_by_multiple_field_unique,
                fields=["employee_id","location_lat","location_long"],
                match_values=[employee_id, location_lat, location_long],
                error_not_exist=False,
            )
        )
