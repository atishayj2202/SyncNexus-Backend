from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.responses import Response

from src.auth import relation, user_auth
from src.auth.relation import VerifiedEmployee
from src.auth.user_auth import VerifiedTask, VerifiedUser
from src.client.cockroach import CockroachDBClient
from src.responses.employee import EmployeeResponse
from src.responses.job import JobCreateRequest, JobResponse
from src.responses.task import TaskCreateRequest
from src.responses.user import PaymentRequest, PaymentResponse, UserResponse
from src.responses.util import DurationRequest, Location
from src.services.employer import EmployerService
from src.utils.client import getCockroachClient

EMPLOYER_PREFIX = "/employer"
employer_router = APIRouter(prefix=EMPLOYER_PREFIX)
ENDPOINT_ADD_TASK = "/add-task/"  # done | integrated
ENDPOINT_ADD_JOBS = "/add-jobs/"  # done | integrated
ENDPOINT_GET_EMPLOYEES = "/get-employees/"  # done  | integrated
ENDPOINT_GET_EMPLOYEE = "/{employee_id}/get-employee/"  # done | integrated
ENDPOINT_GET_EMPLOYEE_LOCATION = (
    "/{employee_id}/get-employee-location/"  # done | integrated
)
ENDPOINT_ADD_EMPLOYEE = "/{employee_id}/add-employee/{title}"  # done | integrated
ENDPOINT_SEARCH_EMPLOYEE_PHONE = (
    "/{phone_no}/search-employee-phone/"  # done | integrated
)
ENDPOINT_SEARCH_EMPLOYEE_EMAIL = (
    "/{email_id}/search-employee-email/"  # done | integrated
)
ENDPOINT_REMOVE_EMPLOYEE = "/{employee_id}/remove-employee/"  # done | integrated
ENDPOINT_ADD_PAYMENT = "/{employee_id}/add-payment/"  # done | integrated
ENDPOINT_GET_EMPLOYEE_PAYMENT = "/{employee_id}/get-payment/"  # done | integrated
ENDPOINT_GET_JOBS = "/get-jobs/"  # done | integrated
ENDPOINT_DELETE_TASK = "/{task_id}/delete-task/"  # done | integrated
ENDPOINT_DELETE_JOB = "/{job_id}/delete-job/"  # done | integrated
ENDPOINT_COMPLETE_JOB = "/{job_id}/complete-job/"  # done | integrated


@employer_router.post(ENDPOINT_ADD_TASK)
async def post_add_task(
    request: TaskCreateRequest,
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
    verified_user: VerifiedUser = Depends(user_auth.verify_employer),
):
    EmployerService.add_task(request, cockroach_client, verified_user.requesting_user)
    return Response(status_code=status.HTTP_200_OK)


@employer_router.get(ENDPOINT_ADD_EMPLOYEE)
async def get_add_employee(
    employee_id: UUID,
    title: str,
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
    verified_user: VerifiedUser = Depends(user_auth.verify_employer),
):
    if verified_user.requesting_user.id == employee_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You cannot add yourself as an employee",
        )
    EmployerService.add_employee(
        employee_id=employee_id,
        cockroach_client=cockroach_client,
        user=verified_user.requesting_user,
        title=title,
    )
    return Response(status_code=status.HTTP_200_OK)


@employer_router.post(ENDPOINT_ADD_JOBS)
async def post_add_job(
    request: JobCreateRequest,
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
    verified_user: VerifiedUser = Depends(user_auth.verify_employer),
):
    EmployerService.add_job(request, cockroach_client, verified_user.requesting_user)
    return Response(status_code=status.HTTP_200_OK)


@employer_router.get(ENDPOINT_GET_EMPLOYEES, response_model=list[EmployeeResponse])
async def get_employees(
    verified_user: VerifiedUser = Depends(user_auth.verify_employer),
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
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
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
):
    return EmployerService.search_employee_by_phone(
        cockroach_client=cockroach_client, phone_no=phone_no
    )


@employer_router.get(
    ENDPOINT_SEARCH_EMPLOYEE_EMAIL,
    response_model=UserResponse,
    dependencies=[Depends(user_auth.verify_employer)],
)
async def get_search_employees_by_email(
    email_id: str,
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
):
    return EmployerService.search_employee_by_email(
        cockroach_client=cockroach_client, email=email_id
    )


@employer_router.post(ENDPOINT_GET_EMPLOYEE_LOCATION, response_model=list[Location])
async def post_get_employee_location(
    request: DurationRequest,
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
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
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
    verified_employee: VerifiedEmployee = Depends(relation.verify_employee_s_employer),
):
    if verified_employee.employer is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to add payment to this employee",
        )
    EmployerService.add_payment(
        user=verified_employee.employer,
        employee_id=verified_employee.employee.id,
        request=request,
        cockroach_client=cockroach_client,
    )
    return Response(status_code=status.HTTP_200_OK)


@employer_router.get(
    ENDPOINT_GET_EMPLOYEE_PAYMENT, response_model=list[PaymentResponse]
)
async def post_get_employee_payment(
    employee_id: UUID,
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
    verified_user: VerifiedUser = Depends(user_auth.verify_employer),
):
    return EmployerService.fetch_employee_payments(
        cockroach_client=cockroach_client,
        user=verified_user.requesting_user,
        user_id=employee_id,
    )


@employer_router.get(ENDPOINT_REMOVE_EMPLOYEE)
async def get_remove_employee(
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
    verified_employee: VerifiedEmployee = Depends(relation.verify_employee_s_employer),
):
    if verified_employee.employer is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to add payment to this employee",
        )
    EmployerService.remove_employee(
        cockroach_client=cockroach_client,
        user_employee=verified_employee.employee,
        user_employer=verified_employee.employer,
    )
    return Response(status_code=status.HTTP_200_OK)


@employer_router.get(ENDPOINT_GET_EMPLOYEE, response_model=EmployeeResponse)
async def get_employee(
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
    verified_employee: VerifiedEmployee = Depends(relation.verify_employee_s_employer),
):
    return EmployerService.fetch_employee(
        cockroach_client=cockroach_client, user=verified_employee.employee
    )


@employer_router.get(ENDPOINT_DELETE_JOB)
async def get_delete_job(
    job_id: UUID,
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
    verified_user: VerifiedUser = Depends(user_auth.verify_employer),
):
    EmployerService.delete_job(
        job_id=job_id,
        cockroach_client=cockroach_client,
        user=verified_user.requesting_user,
    )
    return Response(status_code=status.HTTP_200_OK)


@employer_router.get(ENDPOINT_COMPLETE_JOB)
async def get_complete_job(
    job_id: UUID,
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
    verified_user: VerifiedUser = Depends(user_auth.verify_employer),
):
    EmployerService.complete_job(
        job_id=job_id,
        cockroach_client=cockroach_client,
        user=verified_user.requesting_user,
    )
    return Response(status_code=status.HTTP_200_OK)


@employer_router.get(ENDPOINT_GET_JOBS, response_model=list[JobResponse])
async def get_jobs(
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
    verified_user: VerifiedUser = Depends(user_auth.verify_employer),
):
    return EmployerService.get_jobs(
        cockroach_client=cockroach_client, user=verified_user.requesting_user
    )


@employer_router.get(ENDPOINT_DELETE_TASK)
async def get_delete_task(
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
    verified_task: VerifiedTask = Depends(user_auth.verify_task),
):
    EmployerService.delete_task(
        task=verified_task.task,
        cockroach_client=cockroach_client,
        user=verified_task.requesting_user,
    )
    return Response(status_code=status.HTTP_200_OK)
