from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.responses import Response

from src.auth import relation, user_auth
from src.auth.relation import VerifiedEmployee
from src.auth.user_auth import VerifiedUser
from src.client.cockroach import CockroachDBClient
from src.responses.employee import EmployeeCreateRequest
from src.responses.job import JobCreateRequest
from src.responses.task import TaskCreateRequest
from src.responses.util import DurationRequest
from src.services.employer import EmployerService

EMPLOYER_PREFIX = "/employee"
employee_router = APIRouter(prefix=EMPLOYER_PREFIX)
ENDPOINT_ADD_TASK = "/add-task/"  # done
ENDPOINT_ADD_EMPLOYEE = "/add-employee/"  # done
ENDPOINT_ADD_JOBS = "/add-jobs/"  # done
ENDPOINT_GET_EMPLOYEES = "/get-employees/"  # done
ENDPOINT_GET_EMPLOYEE = "/{employee_id}/get-employee/"  # pending
ENDPOINT_GET_EMPLOYEE_LOCATION = "/{employee_id}/get-employee-location/"  # pending
ENDPOINT_SEARCH_EMPLOYEE = "/{phone_no}/search-employee/"  # done
ENDPOINT_REMOVE_EMPLOYEE = "/{employee_id}/remove-employee/"  # pending


@employee_router.post(ENDPOINT_ADD_TASK)
async def post_add_task(
    request: TaskCreateRequest,
    cockroach_client: CockroachDBClient = Depends(),
    verified_user: VerifiedUser = Depends(user_auth.verify_employer),
):
    EmployerService.add_task(request, cockroach_client, verified_user.requesting_user)
    return Response(status_code=status.HTTP_200_OK)


@employee_router.post(ENDPOINT_ADD_EMPLOYEE)
async def post_add_employee(
    request: EmployeeCreateRequest,
    cockroach_client: CockroachDBClient = Depends(),
    verified_user: VerifiedUser = Depends(user_auth.verify_employer),
):
    if verified_user.requesting_user.id == request.employee_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You cannot add yourself as an employee",
        )
    EmployerService.add_employee(request, cockroach_client)
    return Response(status_code=status.HTTP_200_OK)


@employee_router.post(ENDPOINT_ADD_JOBS)
async def post_add_job(
    request: JobCreateRequest,
    cockroach_client: CockroachDBClient = Depends(),
    verified_user: VerifiedUser = Depends(user_auth.verify_employer),
):
    EmployerService.add_job(request, cockroach_client, verified_user.requesting_user)
    return Response(status_code=status.HTTP_200_OK)


@employee_router.get(ENDPOINT_GET_EMPLOYEES)
async def get_employees(
    verified_user: VerifiedUser = Depends(user_auth.verify_employer),
    cockroach_client: CockroachDBClient = Depends(),
):
    return EmployerService.fetch_employees(
        cockroach_client=cockroach_client, user=verified_user.requesting_employee
    )


@employee_router.get(ENDPOINT_SEARCH_EMPLOYEE)
async def get_search_employees(
    phone_no: str,
    verified_user: VerifiedUser = Depends(user_auth.verify_employer),
    cockroach_client: CockroachDBClient = Depends(),
):
    return EmployerService.search_employee(
        cockroach_client=cockroach_client, phone_no=phone_no
    )


@employee_router.post(ENDPOINT_GET_EMPLOYEE_LOCATION)
async def post_get_employee_location(
    employee_id: UUID,
    request: DurationRequest,
    cockroach_client: CockroachDBClient = Depends(),
    verified_employee: VerifiedEmployee = Depends(relation.verify_employee_s_employer),
):
    return EmployerService.fetch_location_path(
        cockroach_client=cockroach_client,
        user=verified_employee.employee,
        request=request,
    )
