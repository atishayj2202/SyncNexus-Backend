from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import Response

EMPLOYEE_PREFIX = "/employee"
employee_router = APIRouter(prefix=EMPLOYEE_PREFIX)
ENDPOINT_GET_TASKS = "/get-tasks/"  # pending
ENDPOINT_GET_TASK = "/{task_id}/get-task/"  # pending
ENDPOINT_GET_JOB_DESCRIPTION = "/{task_id}/get-job-description/"  # pending
ENDPOINT_COMPLETE_TASK = "/{task_id}/complete-task/"  # pending
ENDPOINT_GET_EMPLOYER = "/{employer_id}/get-employer/"  # pending
ENDPOINT_ADD_LOCATION = "/add-location/"  # pending
ENDPOINT_GET_JOBS = "/get-jobs/"  # pending
