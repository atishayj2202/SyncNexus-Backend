from click import UUID
from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import Response

from src.auth import relation, user_auth
from src.auth.relation import VerifiedEmployee
from src.auth.user_auth import VerifiedTask, VerifiedUser
from src.client.cockroach import CockroachDBClient
from src.responses.util import DurationRequest
from src.services.employee import EmployeeService

EMPLOYEE_PREFIX = "/employee"
employee_router = APIRouter(prefix=EMPLOYEE_PREFIX)
ENDPOINT_GET_TASKS = "/{employee_id}/get-tasks/"  # done
ENDPOINT_GET_TASK = "/{task_id}/get-task/"  # done
ENDPOINT_GET_JOB_DETAIL = "/{job_id}/get-job-detail/"  # pending
ENDPOINT_COMPLETE_TASK = "/{task_id}/complete-task/"  # pending
ENDPOINT_GET_EMPLOYER = "/{employer_id}/get-employer/"  # pending
ENDPOINT_ADD_LOCATION = "/add-location/"  # pending
ENDPOINT_GET_JOBS = "/get-jobs/"  # pending
ENDPOINT_LEAVE_JOB = "/leave-job/"  # pending


@employee_router.post(ENDPOINT_GET_TASKS)
async def get_tasks(
    employee_id: UUID,
    request: DurationRequest,
    cockroach_client: CockroachDBClient = Depends(),
    verified_employee: VerifiedEmployee = Depends(relation.verify_employee_s_employer),
):
    return EmployeeService.fetch_tasks(
        verified_employee.employee, cockroach_client, request
    )


@employee_router.get(ENDPOINT_GET_TASK)
async def get_task(
    task_id: UUID,
    verified_task: VerifiedTask = Depends(user_auth.verify_task),
):
    return EmployeeService.fetch_task(verified_task.task)


@employee_router.get(ENDPOINT_LEAVE_JOB)
async def get_leave_job(
    verified_user: VerifiedUser = Depends(user_auth.verify_employee),
    cockroach_client: CockroachDBClient = Depends(),
):
    EmployeeService.leave_job(cockroach_client, verified_user.requesting_user)
    return Response(status_code=status.HTTP_200_OK)
