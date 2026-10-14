
# CloudOps Pro

### Containerized DevOps Control Center

CloudOps Pro is a Dockerized task management and operations dashboard built to demonstrate practical DevOps engineering workflows.

The application combines a FastAPI backend, PostgreSQL database, and responsive web dashboard in a reproducible Docker Compose environment.

## Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI |
| Database | PostgreSQL 17 |
| Frontend | HTML, CSS, Vanilla JavaScript |
| Containers | Docker, Docker Compose |
| Database Access | psycopg, parameterized SQL |
| Development | Ubuntu WSL2, VS Code |
| CI/CD | Planned |
| Infrastructure as Code | Planned |
| Kubernetes | Planned |

## Features

- Create, view, update, and delete tasks
- Task priorities and workflow statuses
- Dashboard with task statistics
- FastAPI REST endpoints
- PostgreSQL persistent storage
- Multi-stage Docker image
- Non-root application container
- Database container health check
- Responsive dark-themed interface

## Architecture

```text
            Web Browser
                 |
       http://localhost:8000
                 |
          Docker Compose
                 |
         +-------v--------+
         | FastAPI        |
         | Dashboard      |
         | Container      |
         | Non-root User  |
         +-------+--------+
                 |
         Docker Backend
             Network
                 |
         +-------v--------+
         | PostgreSQL 17  |
         | Container      |
         +-------+--------+
                 |
         Persistent Volume
          postgres_data
```

The API is exposed only through `127.0.0.1:8000`. PostgreSQL is accessible to services on the Docker network and does not publish its database port to the host.

## Project Structure

```text
cloudops-pro/
├── app/
│   ├── api/
│   ├── db/
│   ├── schemas/
│   ├── services/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── templates/
│   └── main.py
├── sql/
│   └── init.sql
├── Dockerfile
├── compose.yaml
├── requirements.txt
├── requirements-prod.txt
├── .dockerignore
├── .gitignore
├── .env.example
└── README.md
```

## Local Setup

### Requirements

- Docker Engine or Docker Desktop
- Docker Compose

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd cloudops-pro
```

Replace the placeholder URL with the published GitHub repository URL.

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set a strong, unique PostgreSQL password before first startup.

Never commit `.env` or real credentials.

### 3. Build and start

```bash
docker compose up -d --build
```

### 4. Initialize the database

For a fresh database, apply the provided SQL schema:

```bash
docker compose exec -T db sh -c \
  'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' \
  < sql/init.sql
```

Run schema initialization only for a new database. Review the SQL file before executing it against an existing database.

### 5. Open the application

Dashboard:

http://127.0.0.1:8000

FastAPI interactive documentation:

http://127.0.0.1:8000/docs

Health endpoint:

http://127.0.0.1:8000/health/live

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health/live` | API liveness |
| GET | `/api/v1/tasks` | List tasks |
| POST | `/api/v1/tasks` | Create task |
| GET | `/api/v1/tasks/{task_id}` | Get task |
| PATCH | `/api/v1/tasks/{task_id}` | Update task |
| DELETE | `/api/v1/tasks/{task_id}` | Delete task |

The liveness endpoint checks that the API process responds. It does not independently verify database readiness.

## Docker Commands

Start services:

```bash
docker compose up -d
```

View service status:

```bash
docker compose ps
```

Check API health:

```bash
curl -i http://127.0.0.1:8000/health/live
```

View API logs:

```bash
docker compose logs --tail=100 api
```

Stop services without deleting persistent data:

```bash
docker compose down
```

Do not use `docker compose down -v` unless you intentionally want to remove the database volume.

## Docker Optimization

The API image uses a multi-stage Docker build.

- Dependencies are installed in a separate builder stage.
- The final image includes production requirements.
- The application runs as non-root UID 10001.
- Development files are excluded through `.dockerignore`.

Measured image sizes:

| Stage | Image Size |
|---|---:|
| Original image | 276 MB |
| Production dependency optimization | 241 MB |
| Base image refresh | 230 MB |

Total reduction: approximately 16.7%.

## Security Review

Security measures implemented:

- Non-root API container
- Localhost-only API port binding
- PostgreSQL port not published
- Database health checks
- Secrets excluded from Git
- Separate Docker network
- Multi-stage Docker build

### Docker Scout Findings

After refreshing the Python base image, the scan reported:

| Severity | Findings |
|---|---:|
| Critical | 0 |
| High | 1 |
| Medium | 6 |
| Low | 27 |

The remaining High finding was reported as `CVE-2026-85091` affecting Debian zlib. Docker Scout did not display a fixed version at the time of review.

These figures describe a scan snapshot, not a guarantee that the image is vulnerability-free. Vulnerabilities require continued monitoring and remediation.

### Deployment Considerations

This repository demonstrates a local development environment. It is not a hardened public production deployment.

Before exposing the application publicly, additional controls are required, including authentication, HTTPS, secret management, access restrictions, and production deployment security reviews.

## Roadmap

- [x] FastAPI task management application
- [x] PostgreSQL integration
- [x] Responsive operations dashboard
- [x] Docker Compose deployment
- [x] Docker image optimization
- [x] Initial vulnerability review
- [ ] Automated testing and CI/CD with GitHub Actions
- [ ] Terraform infrastructure provisioning
- [ ] Kubernetes deployment
- [ ] Final deployment documentation and evidence

## Project Purpose

Developed as a hands-on DevOps portfolio project demonstrating containerization, application delivery, automation, infrastructure provisioning, and Kubernetes deployment.

## Author

Marriam Tahir

DevOps Engineering | Cloud Infrastructure | Automation

