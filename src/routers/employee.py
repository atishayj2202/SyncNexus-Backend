from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import Response

from src.auth import relation, user_auth
from src.auth.relation import VerifiedEmployee
from src.auth.user_auth import VerifiedTask, VerifiedUser
from src.client.cockroach import CockroachDBClient
from src.responses.employee import EmployeeResponse
from src.responses.job import JobResponse
from src.responses.task import TaskResponse
from src.responses.user import UserResponse
from src.responses.util import DurationRequest, Location
from src.services.employee import EmployeeService
from src.utils.client import getCockroachClient

EMPLOYEE_PREFIX = "/employee"
employee_router = APIRouter(prefix=EMPLOYEE_PREFIX)
ENDPOINT_GET_TASKS = "/{employee_id}/get-tasks/"  # done | integrated
ENDPOINT_GET_TASK = "/{task_id}/get-task/"  # done | integrated
ENDPOINT_GET_JOB_DETAIL = "/{job_id}/get-job-detail/"  # done | integrated
ENDPOINT_COMPLETE_TASK = "/{task_id}/complete-task/"  # done | integrated
ENDPOINT_GET_EMPLOYER = "/get-employer/"  # done | integrated
ENDPOINT_ADD_LOCATION = "/add-location/"  # done | integrated
ENDPOINT_FIND_JOBS = "/find-jobs/"  # done | integrated
ENDPOINT_LEAVE_JOB = "/leave-job/"  # done | integrated
ENDPOINT_APPROVE_PAYMENT = "/{payment_id}/approve-payment/"  # done | integrated
ENDPOINT_GET_EMPLOYEE_JOB = "/get-employee-job/"  # done


@employee_router.post(ENDPOINT_GET_TASKS, response_model=list[TaskResponse])
async def get_tasks(
    request: DurationRequest,
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
    verified_employee: VerifiedEmployee = Depends(relation.verify_employee_s_employer),
):
    return EmployeeService.fetch_tasks(
        verified_employee.employee, cockroach_client, request
    )


@employee_router.get(ENDPOINT_GET_TASK, response_model=TaskResponse)
async def get_task(
    verified_task: VerifiedTask = Depends(user_auth.verify_task),
):
    return EmployeeService.fetch_task(verified_task.task)


@employee_router.get(ENDPOINT_LEAVE_JOB)
async def get_leave_job(
    verified_user: VerifiedUser = Depends(user_auth.verify_employee),
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
):
    EmployeeService.leave_job(
        cockroach_client=cockroach_client, user=verified_user.requesting_user
    )
    return Response(status_code=status.HTTP_200_OK)


@employee_router.get(ENDPOINT_COMPLETE_TASK)
async def get_complete_task(
    verified_task: VerifiedTask = Depends(user_auth.verify_task),
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
):
    EmployeeService.complete_task(verified_task.task, cockroach_client)
    return Response(status_code=status.HTTP_200_OK)


@employee_router.post(ENDPOINT_ADD_LOCATION)
async def post_add_location(
    location: Location,
    verified_user: VerifiedUser = Depends(user_auth.verify_employee),
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
):
    EmployeeService.add_location(
        location=location,
        user=verified_user.requesting_user,
        cockroach_client=cockroach_client,
    )
    return Response(status_code=status.HTTP_200_OK)


@employee_router.post(
    ENDPOINT_FIND_JOBS,
    response_model=list[JobResponse],
    dependencies=[Depends(user_auth.verify_employee)],
)
async def post_get_jobs(
    request: Location,
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
):
    return EmployeeService.get_jobs(cockroach_client=cockroach_client, request=request)


@employee_router.get(
    ENDPOINT_GET_JOB_DETAIL,
    response_model=JobResponse,
    dependencies=[Depends(user_auth.verify_employee)],
)
async def get_job_detail(
    job_id: UUID,
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
):
    return EmployeeService.fetch_job(cockroach_client=cockroach_client, job_id=job_id)


@employee_router.get(ENDPOINT_APPROVE_PAYMENT)
async def get_approve_payment(
    payment_id: UUID,
    verified_user: VerifiedUser = Depends(user_auth.verify_employee),
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
):
    EmployeeService.approve_payment(
        payment_id=payment_id,
        user=verified_user.requesting_user,
        cockroach_client=cockroach_client,
    )
    return Response(status_code=status.HTTP_200_OK)


@employee_router.get(ENDPOINT_GET_EMPLOYER, response_model=UserResponse)
async def get_employer(
    verified_user: VerifiedUser = Depends(user_auth.verify_employee),
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
):
    return EmployeeService.fetch_employer(
        cockroach_client=cockroach_client, user=verified_user.requesting_user
    )


@employee_router.get(ENDPOINT_GET_EMPLOYEE_JOB, response_model=EmployeeResponse)
async def get_employee_job(
    verified_user: VerifiedUser = Depends(user_auth.verify_employee),
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
):
    return EmployeeService.fetch_employee_job(
        cockroach_client=cockroach_client, user=verified_user.requesting_user
    )
