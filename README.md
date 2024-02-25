# SyncNexus Backend - Google Solution Challenge

Welcome to the SyncNexus backend repository for the Google Solution Challenge! This backend repository serves as the core infrastructure powering the SyncNexus platform, facilitating seamless communication between users, managing job listings, and handling various other functionalities.

## Project Links

This section contains links to the frontend and backend repositories, as well as the base URL and documentation for the backend API.

### Frontend Repository
- Repository URL: [Frontend Repo - https://github.com/Ahmedazim7804/SyncNexus-Frontend](https://github.com/Ahmedazim7804/SyncNexus-Frontend)

### Backend Repository
- Repository URL: [Backend Repo - https://github.com/atishayj2202/SyncNexus-Backend](https://github.com/atishayj2202/SyncNexus-Backend)

### Backend API Endpoint Base URL
- Base URL: https://google-solution-challenge-backend-jpnacpp5ta-em.a.run.app

### Backend API Endpoint Documentation
- Documentation URL: https://google-solution-challenge-backend-jpnacpp5ta-em.a.run.app/docs

## Technologies Used
- **Programming Language**: Python
- **Framework**: fastAPI
- **Database**: PostgresSQL(Google Cloud SQL)
- **Authentication**: Firebase Authentication
- **Deployment**: Google Cloud Run
- **Poetry**: Poetry is used as the dependency manager for managing Python packages and dependencies.

## Project Structure
The backend project follows a standard fastAPI project structure with modular apps for different functionalities. Here's an overview of the main components:
- **auth**: This directory contains modules related to authentication, including functions for handling authentication for each request.
- **client**: Here resides the client modules for Firebase Authentication and database. It provides functionalities to interact with Firebase services.
- **db**: This directory handles the database interactions and includes the schema definition for each table and view. 
  - The base.py file contains the parent Schema and basic algorithms for each table. 
  - The tables subdirectory contains schema definitions for various database tables, while the views subdirectory contains schema definitions for database views.
- **responses**: Contains schema definitions for requests and responses. This helps maintain a structured approach to handling data exchanges.
- **routers**: Contains router modules for FastAPI. These routers define the API endpoints and link them to appropriate handlers.
- **services**: Includes algorithms to handle queries in the database and return data. These services encapsulate business logic related to data manipulation.
- **main.py**: This is the entry point of the application. It connects all routers to FastAPI, initializing the web server and defining routes.

## Architecture
![architecture.jpg](public%2Farchitecture.jpg)

## Setup Instructions
To set up the backend locally for development or testing purposes, follow these steps:
1. **Run Migrations**: Execute database migrations using the migration file located at `deploy/flyway/migrations` to ensure the database schema is up-to-date.
2. **Setup Virtual Environment**: Create and activate a virtual environment using Poetry. Use the following commands:
   ```shell
   poetry env use ~/.pyenv/versions/3.10.12/bin/python
   poetry install
   ```
3. **Add Firebase and Google Cloud Keys**: Place the Firebase Key (JSON) and Service Account Key (JSON) of Google Cloud in the `keys` folder.
4. **Download Client for Google Cloud SQL**: Download the client to access Google Cloud SQL. This is a one-time step. Use the following command:
   ```shell
   sh deploy/local_test.sh pull-auth-proxy
   ```
5. **Update SQL Connection and Credentials**: Update the SQL connection details and credentials file path in `deploy/local_test.sh`. Run the following command to start the database for running the backend:
    ```shell
   sh deploy/local_test.sh remote-start-test
   ```
6. **Setup Environment Variables**: Define the following environment variables:
   - *CORS_ORIGINS*: Specify all origins (URLs) separated by commas.
   - *DB_NAME*: Name of the database.
   - *DB_USER*: User of the database.
   - *DB_PASS*: Password of the above user.
   - *UNIX_SOCKET_PATH*: Path of the Unix socket file. By default, it's "./keys/" + `connection string of the database`.
   - *FIREBASE_API_KEY*: API key of Firebase.
   - *FIREBASE_SA_KEY_PATH*: Absolute path of the Firebase credentials file.
7. **Run Backend Server**: Execute the src/main.py file to start the backend server.

## Deployment Instructions
The backend is designed to be deployed on Google Cloud Platform (GCP) for scalability, reliability, and performance. Follow these steps for deployment:
##### Prerequisites
- Docker Daemon installed.
- Access to a remote location to upload Docker images (e.g., Docker Hub, Google Artifact Registry).

##### Build, Push & Deploy Docker Image
1. Update credentials in the `deploy.sh` file.
2. Run the following command to build and push the Docker image:
```shell
sh deploy/local_test.sh remote-start-test
   ```
3. Host Image on Google Cloud Run. Ensure the following secrets and file mounts are configured when hosting the image on Google Cloud Run:
   - *CORS_ORIGINS*: Specify all origins (URLs) separated by commas.
   - *DB_NAME*: Name of the database.
   - *DB_USER*: User of the database.
   - *DB_PASS*: Password of the above user.
   - *UNIX_SOCKET_PATH*: Path of the Unix socket file. By default, it's the connection string of the database.
   - *FIREBASE_API_KEY*: API key of Firebase.
   - *FIREBASE_SA_KEY_PATH*: Absolute path of the Firebase credentials file(This file needs to be mounted on image).

## Linting/Formatting
The following commands can be used:

```shell
poetry run sh deploy/local_test.sh check-format
poetry run sh deploy/local_test.sh format
```

## Bumpversion

```shell
poetry run bumpversion --config-file=./deploy/.bumpversion.cfg <option>
```
The option can be:
- patch: to update the patch version
- minor: to update the minor version
- major: to update the major version
- release: to update the release version
  - also add `--tag` to create a git tag when releasing

## Contributors
- Atishaya Jain
- Ajeem Ahmed
- Sidhhant Gudwani
- Tanmay Gupta
