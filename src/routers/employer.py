from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import Response

EMPLOYER_PREFRIX = "/employee"
employee_router = APIRouter(prefix=EMPLOYER_PREFRIX)
ENDPOINT_ADD_TASK = "/add-task/"  # pending
ENDPOINT_ADD_EMPLOYEE = "/add-employee/"  # pending
ENDPOINT_ADD_JOBS = "/add-jobs/"  # pending
ENDPOINT_GET_EMPLOYEES = "/get-employees/"  # pending
ENDPOINT_GET_EMPLOYEE = "/{employee_id}/get-employee/"  # pending