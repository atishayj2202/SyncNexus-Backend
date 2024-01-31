from fastapi import HTTPException
from starlette import status

from src.client.cockroach import CockroachDBClient
from src.db.tables.employee_mapping import Employee_Mapping
from src.db.tables.task import Task
from src.db.tables.user import User
from src.responses.task import TaskResponse
from src.responses.util import DurationRequest
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
        tasks: list[Task] = cockroach_client.query(
            Task.get_by_field_multiple,
            field="employee_id",
            match_value=employee.id,
            error_not_exist=False,
        )
        response_list = []
        for task in tasks:
            if request.start_time < task.last_date < request.end_time:
                continue
            response_list.append(cls.fetch_task(task))
        return response_list

    @classmethod
    def leave_job(cls, cockroach_client: CockroachDBClient, user: User):
        employee_mapping = cockroach_client.query(
            Employee_Mapping.get_by_multiple_field_unique,
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
            Employee_Mapping.update_by_id,
            id=employee_mapping.id,
            new_data=employee_mapping,
        )
