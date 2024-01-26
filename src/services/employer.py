from uuid import UUID

from src.client.cockroach import CockroachDBClient
from src.db.employee_mapping import Employee_Mapping
from src.db.task import Task
from src.db.user import User
from src.responses.task import TaskCreateRequest


class EmployerService:
    """@classmethod
    def __verify_employee(cls, employee_id: UUID, employer: User, cockroach_client: CockroachDBClient) -> None:
        employee = cockroach_client.query(User.get_id(), id=employee_id,error_not_exist=False)
        if employee is None:
            raise Exception("Employee not found")
        if employee.employer_id != employer.id:
            raise Exception("Employee not found")"""

    @classmethod
    def add_task(
        cls, request: TaskCreateRequest, cockroach_client: CockroachDBClient, user: User
    ) -> None:
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
