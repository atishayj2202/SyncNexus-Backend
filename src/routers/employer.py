from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.responses import Response

from src.auth import relation, user_auth
from src.auth.relation import VerifiedEmployee
from src.auth.user_auth import VerifiedUser
from src.client.cockroach import CockroachDBClient
from src.responses.employee import EmployeeResponse
from src.responses.job import JobCreateRequest
from src.responses.task import TaskCreateRequest
from src.responses.user import PaymentRequest, UserResponse
from src.responses.util import DurationRequest, Location
from src.services.employer import EmployerService

EMPLOYER_PREFIX = "/employer"
employer_router = APIRouter(prefix=EMPLOYER_PREFIX)
ENDPOINT_ADD_TASK = "/add-task/"  # done
ENDPOINT_ADD_JOBS = "/add-jobs/"  # done
ENDPOINT_GET_EMPLOYEES = "/get-employees/"  # done
ENDPOINT_GET_EMPLOYEE = "/{employee_id}/get-employee/"  # pending
ENDPOINT_GET_EMPLOYEE_LOCATION = "/{employee_id}/get-employee-location/"  # done
ENDPOINT_ADD_EMPLOYEE = "/{employee_id}/add-employee/{title}"  # done
ENDPOINT_SEARCH_EMPLOYEE_PHONE = "/{phone_no}/search-employee-phone/"  # done
ENDPOINT_SEARCH_EMPLOYEE_EMAIL = "{email_id}/search-user-email/"  # pending
ENDPOINT_REMOVE_EMPLOYEE = "/{employee_id}/remove-employee/"  # pending
ENDPOINT_ADD_PAYMENT = "/{employee_id}/add-payment/"  # done
ENDPOINT_GET_EMPLOYEE_PAYMENT = "/{employee_id}/get-payment/"  # done


@employer_router.post(ENDPOINT_ADD_TASK)
async def post_add_task(
    request: TaskCreateRequest,
    cockroach_client: CockroachDBClient = Depends(),
    verified_user: VerifiedUser = Depends(user_auth.verify_employer),
):
    EmployerService.add_task(request, cockroach_client, verified_user.requesting_user)
    return Response(status_code=status.HTTP_200_OK)


@employer_router.post(ENDPOINT_ADD_EMPLOYEE)
async def get_add_employee(
    employee_id: UUID,
    title: str,
    cockroach_client: CockroachDBClient = Depends(),
    verified_user: VerifiedUser = Depends(user_auth.verify_employer),
):
    if verified_user.requesting_user.id == employee_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You cannot add yourself as an employee",
        )
    EmployerService.add_employee(
        employee_id, cockroach_client, verified_user.requesting_user
    )
    return Response(status_code=status.HTTP_200_OK)


@employer_router.post(ENDPOINT_ADD_JOBS)
async def post_add_job(
    request: JobCreateRequest,
    cockroach_client: CockroachDBClient = Depends(),
    verified_user: VerifiedUser = Depends(user_auth.verify_employer),
):
    EmployerService.add_job(request, cockroach_client, verified_user.requesting_user)
    return Response(status_code=status.HTTP_200_OK)


@employer_router.get(ENDPOINT_GET_EMPLOYEES, response_model=list[EmployeeResponse])
async def get_employees(
    verified_user: VerifiedUser = Depends(user_auth.verify_employer),
    cockroach_client: CockroachDBClient = Depends(),
):
    return EmployerService.fetch_employees(
        cockroach_client=cockroach_client, user=verified_user.requesting_user
    )


@employer_router.get(
    ENDPOINT_SEARCH_EMPLOYEE_PHONE,
    response_model=UserResponse,
    dependencies=[Depends(user_auth.verify_employer)],
)
async def get_search_employees(
    phone_no: str,
    cockroach_client: CockroachDBClient = Depends(),
):
    return EmployerService.search_employee(
        cockroach_client=cockroach_client, phone_no=phone_no
    )


@employer_router.post(ENDPOINT_GET_EMPLOYEE_LOCATION, response_model=list[Location])
async def post_get_employee_location(
    request: DurationRequest,
    cockroach_client: CockroachDBClient = Depends(),
    verified_employee: VerifiedEmployee = Depends(relation.verify_employee_s_employer),
):
    return EmployerService.fetch_location_path(
        cockroach_client=cockroach_client,
        user=verified_employee.employee,
        request=request,
    )


@employer_router.post(ENDPOINT_ADD_PAYMENT)
async def post_add_payment(
    request: PaymentRequest,
    cockroach_client: CockroachDBClient = Depends(),
    verified_employee: VerifiedEmployee = Depends(relation.verify_employee_s_employer),
):
    if verified_employee.employer is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to add payment to this employee",
        )
    EmployerService.add_payment(
        user=verified_employee.employer,
        request=request,
        cockroach_client=cockroach_client,
    )


@employer_router.get(ENDPOINT_GET_EMPLOYEE_PAYMENT)
async def post_get_employee_payment(
    cockroach_client: CockroachDBClient = Depends(),
    verified_employee: VerifiedEmployee = Depends(relation.verify_employee_s_employer),
):
    if verified_employee.employer is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to add payment to this employee",
        )
    EmployerService.fetch_employee_payments(
        cockroach_client=cockroach_client,
        user=verified_employee.employer,
        user_id=verified_employee.employee.id,
    )
    return Response(status_code=status.HTTP_200_OK)
