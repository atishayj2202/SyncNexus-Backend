from uuid import UUID

from fastapi import HTTPException
from starlette import status

from src.client.cockroach import CockroachDBClient
from src.db.tables.employee_location import EmployeeLocation
from src.db.tables.employee_mapping import Employee_Mapping
from src.db.tables.job import Jobs
from src.db.tables.task import Task
from src.db.tables.user import User
from src.responses.job import JobResponse
from src.responses.task import TaskResponse
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

    """@classmethod
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
            created_at=location.datetime
        )"""

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
            last_date=job.last_date,
            done=job.done,
            amount=job.amount,
            deleted=job.deleted,
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
