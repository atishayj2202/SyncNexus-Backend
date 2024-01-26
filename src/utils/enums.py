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
