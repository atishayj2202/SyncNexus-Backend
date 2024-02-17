# SyncNexus Backend - Google Solution Challenge

Welcome to the SyncNexus backend repository for the Google Solution Challenge! This backend repository serves as the core infrastructure powering the SyncNexus platform, facilitating seamless communication between users, managing job listings, and handling various other functionalities.

## Technologies Used
- **Programming Language**: Python
- **Framework**: Django
- **Database**: PostgreSQL
- **Authentication**: Firebase/OAuth 2.0 (e.g., Google Sign-In)
- **API Documentation**: Swagger/OpenAPI
- **Deployment**: Google Cloud Platform (GCP)

## Project Structure
The backend project follows a standard Django project structure with modular apps for different functionalities. Here's an overview of the main components:
- **Users**: Handles user authentication, profile management, and interactions.
- **Jobs**: Manages job listings, job applications, and related operations.
- **Messaging**: Facilitates communication between users through messaging features.
- **Payments**: Handles secure payment processing for job transactions.
- **Utils**: Contains utility functions and helper modules used across the project.

## Setup Instructions
To set up the backend locally for development or testing purposes, follow these steps:
1. Clone the repository: `git clone <repository-url>`
2. Navigate to the project directory: `cd syncnexus-backend`
3. Create and activate a virtual environment: `python3 -m venv venv && source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Set up environment variables (e.g., database credentials, OAuth 2.0 client IDs).
6. Run database migrations: `python manage.py migrate`
7. Create a superuser account: `python manage.py createsuperuser`
8. Start the development server: `python manage.py runserver`

## Deployment
The backend is designed to be deployed on Google Cloud Platform (GCP) for scalability, reliability, and performance. Follow these steps for deployment:
1. Set up a GCP project and enable necessary APIs (e.g., Compute Engine, Cloud SQL).
2. Configure a PostgreSQL database instance on Cloud SQL and connect it to the backend.
3. Set up Cloud Identity-Aware Proxy (IAP) for secure access to the backend APIs.
4. Deploy the Django project using Cloud Run or App Engine, ensuring proper configuration for scalability.
5. Configure environment variables in the deployment environment for sensitive data (e.g., SECRET_KEY, database credentials).

## ENDPOINTS

[//]: # (ENDPOINT_GET_TASKS,)
[//]: # (ENDPOINT_GET_TASK,)
[//]: # (ENDPOINT_GET_JOB_DETAIL,)
[//]: # (ENDPOINT_COMPLETE_TASK,)
[//]: # (ENDPOINT_GET_EMPLOYER,)
[//]: # (ENDPOINT_ADD_LOCATION,)
[//]: # (ENDPOINT_FIND_JOBS,)
[//]: # (ENDPOINT_LEAVE_JOB,)
[//]: # (ENDPOINT_APPROVE_PAYMENT,)
[//]: # (ENDPOINT_GET_EMPLOYEE_JOB)

## Features

1. **Get Tasks (GET /{employee_id}/get-tasks/):**
    - Allows employees to retrieve tasks assigned to them.
    - Facilitates effective task management and tracking.

2. **Get Task (GET /{task_id}/get-task/):**
    - Enables users to access detailed information about a specific task.
    - Provides task description, deadline, and assigned employee details.

3. **Get Job Detail (GET /{job_id}/get-job-detail/):**
    - Allows users to view comprehensive information about a specific job.
    - Provides insights into job requirements, responsibilities, and employer details.

4. **Complete Task (POST /{task_id}/complete-task/):**
    - Enables employees to mark tasks as completed.
    - Facilitates task tracking and progress monitoring for employers.

5. **Get Employer (GET /get-employer/):**
    - Provides users with details about the employer associated with a job.
    - Offers insights into the employer's profile and contact information.

6. **Add Location (POST /add-location/):**
    - Allows users to add location details.
    - Facilitates location-based job search and assignment.

7. **Find Jobs (POST /find-jobs/):**
    - Enables users to search for job opportunities based on various criteria.
    - Offers a tailored job search experience for job seekers and employers.

8. **Leave Job (POST /leave-job/):**
    - Allows employees to resign or discontinue their engagement.
    - Provides a straightforward process for leaving current job positions.

9. **Approve Payment (POST /{payment_id}/approve-payment/):**
    - Enables employers to approve payments for completed tasks or services.
    - Facilitates smooth and timely payment processing for employees.

10. **Get Employee Job (GET /get-employee-job/):**
    - Allows users to retrieve information about job assignments associated with a specific employee.
    - Provides insights into the employee's current job status and assignments.

## API Documentation
The API endpoints are documented using Swagger/OpenAPI specifications. You can access the API documentation by navigating to `/api/docs/` after running the backend locally or deploying it.

## Contributers
Atishay Jain\
Ajeem Ahmed\
Sidhhant Gudwani\
Tanmay Gupta

[//]: # (Contributions to the SyncNexus backend project are welcome! Feel free to open issues for bug reports, feature requests, or submit pull requests with improvements.)

## License
This project is licensed under the [MIT License](LICENSE).
