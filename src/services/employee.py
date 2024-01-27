from src.client.cockroach import CockroachDBClient
from src.db.task import Task
from src.db.user import User
from src.responses.task import TaskResponse
from src.responses.time import DurationRequest
from src.utils.enums import TaskStatus


class EmployeeService:
    @classmethod
    def fetch_tasks(
        cls,
        employee: User,
        cockroach_client: CockroachDBClient,
        request: DurationRequest,
    ) -> list[TaskResponse]:
        tasks: list[Task] = cockroach_client.query(
            Task.get_by_field_multiple,
            field="employee_id",
            match_value=employee.id,
            error_not_exist=False,
        )
        responselist = []
        for task in tasks:
            if request.start_time < task.last_date < request.end_time:
                continue
            temp = TaskStatus.pending
            if task.completed is not None:
                temp = TaskStatus.completed
            elif task.deleted is not None:
                temp = TaskStatus.cancelled
            responselist.append(
                TaskResponse(
                    id=task.id,
                    created_at=task.created_at,
                    employee_id=task.employee_id,
                    employer_id=task.employer_id,
                    heading=task.heading,
                    description=task.description,
                    last_date=task.last_date,
                    status=temp,
                )
            )
        return responselist
