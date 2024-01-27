from click import UUID
from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import Response

from src.auth import relation
from src.auth.relation import VerifiedEmployee
from src.client.cockroach import CockroachDBClient
from src.responses.time import DurationRequest
from src.services.employee import EmployeeService

EMPLOYEE_PREFIX = "/employee"
employee_router = APIRouter(prefix=EMPLOYEE_PREFIX)
ENDPOINT_GET_TASKS = "/{employee_id}/get-tasks/"  # done
ENDPOINT_GET_TASK = "/{task_id}/get-task/"  # pending
ENDPOINT_GET_JOB_DESCRIPTION = "/{task_id}/get-job-description/"  # pending
ENDPOINT_COMPLETE_TASK = "/{task_id}/complete-task/"  # pending
ENDPOINT_GET_EMPLOYER = "/{employer_id}/get-employer/"  # pending
ENDPOINT_ADD_LOCATION = "/add-location/"  # pending
ENDPOINT_GET_JOBS = "/get-jobs/"  # pending


@employee_router.post(ENDPOINT_GET_TASKS)
async def get_tasks(
    employee_id: UUID,
    request: DurationRequest,
    cockroach_client: CockroachDBClient = Depends(),
    verified_employee: VerifiedEmployee = Depends(relation.VerifiedEmployee),
):
    return EmployeeService.fetch_tasks(
        verified_employee.employee, cockroach_client, request
    )
