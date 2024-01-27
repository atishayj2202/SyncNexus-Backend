from uuid import UUID

from fastapi import HTTPException, status

from src.client.cockroach import CockroachDBClient
from src.db.employee_mapping import Employee_Mapping
from src.db.task import Task
from src.db.user import User
from src.responses.task import TaskCreateRequest
from src.responses.employee import EmployeeCreateRequest
from src.responses.job import JobCreateRequest


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
            cls, request: EmployeeCreateRequest, cockroach_client: CockroachDBClient, user: User
    ) -> None:
        cls.__verify_employee(request.employee_id, user, cockroach_client)
        cockroach_client.query(
            Employee.add,
            items=[
                Employee(
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