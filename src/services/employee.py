import datetime

from src.client.cockroach import CockroachDBClient
from src.db.tables import employee_location
from src.db.tables.task import Task
from src.db.tables.user import User
from src.db.tables.job import Jobs
from src.responses.job import JobResponse
from src.responses.task import TaskResponse
from src.responses.util import DurationRequest
from src.responses.util import Location, LocationResponse
from src.utils.enums import TaskStatus


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
    def fetch_job_detail(
            cls,
            job: Jobs
    ) -> JobResponse:
        return JobResponse(
            employer_id=job.employer_id,
            title=job.title,
            description=job.description,
            location_lat=job.location_lat,
            location_long=job.location_long,
            done=job.done,
            amount=job.amount,
            deleted=job.deleted
        )

    @classmethod
    def add_location(
            cls,
            location: employee_location,
    ) -> LocationResponse:
        return LocationResponse(
            employee_id=location.employee_id,
            location=Location(
                location_lat=location.location_lat,
                location_long=location.location_long
            ),
            created_at=location.datetime,
        )
