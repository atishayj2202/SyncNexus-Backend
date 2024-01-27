from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import Response

from src.auth import user_auth
from src.auth.user_auth import VerifiedUser
from src.client.cockroach import CockroachDBClient
from src.responses.employee import EmployeeCreateRequest
from src.responses.job import JobCreateRequest
from src.responses.task import TaskCreateRequest
from src.services.employer import EmployerService

EMPLOYER_PREFIX = "/employee"
employee_router = APIRouter(prefix=EMPLOYER_PREFIX)
ENDPOINT_ADD_TASK = "/add-task/"  # done
ENDPOINT_ADD_EMPLOYEE = "/add-employee/"  # done
ENDPOINT_ADD_JOBS = "/add-jobs/"  # done
ENDPOINT_GET_EMPLOYEES = "/get-employees/"  # pending
ENDPOINT_GET_EMPLOYEE = "/{employee_id}/get-employee/"  # pending
ENDPOINT_GET_EMPLOYEE_LOCATION = "/{employee_id}/get-employee-location/"  # pending


@employee_router.post(ENDPOINT_ADD_TASK)
async def post_add_task(
    request: TaskCreateRequest,
    cockroach_client: CockroachDBClient = Depends(),
    verified_user: VerifiedUser = Depends(user_auth.verify_user),
):
    EmployerService.add_task(request, cockroach_client, verified_user.requesting_user)
    return Response(status_code=status.HTTP_200_OK)


@employee_router.post(ENDPOINT_ADD_EMPLOYEE)
async def post_add_employee(
    request: EmployeeCreateRequest,
    cockroach_client: CockroachDBClient = Depends(),
    verified_user: VerifiedUser = Depends(user_auth.verify_user),
):
    EmployerService.add_employee(
        request, cockroach_client, verified_user.requesting_user
    )
    return Response(status_code=status.HTTP_200_OK)


@employee_router.post(ENDPOINT_ADD_JOBS)
async def post_add_job(
    request: JobCreateRequest,
    cockroach_client: CockroachDBClient = Depends(),
    verified_user: VerifiedUser = Depends(user_auth.verify_user),
):
    EmployerService.add_job(request, cockroach_client, verified_user.requesting_user)
    return Response(status_code=status.HTTP_200_OK)


@employee_router.get(ENDPOINT_GET_EMPLOYEES)
async def get_employees(
    verified_user: VerifiedUser = Depends(user_auth.verify_user),
):
    return EmployerService.fetch_employee(verified_user.requesting_employee)
