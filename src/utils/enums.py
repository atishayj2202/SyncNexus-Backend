from enum import Enum


class AuthType(Enum):
    google = "google"
    facebook = "facebook"
    github = "github"
    apple = "apple"
    email = "email"
    phone = "phone"


class UserType(Enum):
    employee = "employee"
    employer = "employer"


class TaskStatus(Enum):
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"


class EmployeeStatus(Enum):
    active = "active"
    removed = "removed"
    left = "left"
