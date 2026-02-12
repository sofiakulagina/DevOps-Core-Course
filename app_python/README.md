# DevOps Info Service (Lab 1)

## Overview

This project implements a simple **DevOps info service** written in Python using **Flask**. The service exposes HTTP endpoints that return detailed information about the application, the underlying system, and its runtime health. It is the base for later labs (Docker, CI/CD, monitoring, persistence, etc.).

## Prerequisites

- Python 3.11+ (recommended)
- pip (Python package manager)
- Optional: `virtualenv` or `venv` for isolated environments

## Installation

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env_example .env      # create local env file from example
```

## Running the Application

```bash
# Default configuration (HOST=0.0.0.0, PORT=5002, DEBUG=False)
python app.py

# Custom configuration via environment variables
PORT=8080 python app.py
HOST=127.0.0.1 PORT=3000 DEBUG=true python app.py
```

## API Endpoints

- `GET /` – Service and system information
  - Service metadata (name, version, description, framework)
  - System info (hostname, platform, architecture, CPU count, Python version)
  - Runtime info (uptime, current time, timezone)
  - Request info (client IP, user agent, HTTP method, path)
  - List of available endpoints

- `GET /health` – Health check
  - Returns basic health status, timestamp, and uptime in seconds

## Configuration

Configuration is done via environment variables:

| Variable | Default     | Description                           |
|---------|-------------|---------------------------------------|
| `HOST`  | `0.0.0.0`   | Address the Flask app listens on      |
| `PORT`  | `5002`      | TCP port for HTTP server              |
| `DEBUG` | `False`     | Enable Flask debug mode if `true`     |

All configuration is read in `app.py` at startup, so restart the application after changing environment variables.

## Unit Testing

### Framework Choice

For this lab, the project uses Python `unittest`.

Short comparison:
- `pytest`: concise syntax and rich plugin ecosystem, but adds an external dependency.
- `unittest`: part of the Python standard library, no additional package required.

Why `unittest` was chosen:
- Works out of the box in minimal lab environments.
- Keeps dependencies small and predictable.
- Supports fixtures (`setUpClass`) and mocking (`unittest.mock`) needed for endpoint testing.

### Test Structure

Tests are located in `tests/test_app.py` and cover:
- `GET /` success response:
  - expected top-level JSON fields,
  - required nested fields and data types,
  - request metadata (client IP and user-agent handling).
- `GET /health` success response:
  - status, timestamp, uptime checks.
- Error responses:
  - `404` JSON error for unknown route,
  - simulated internal failures for `/` and `/health` returning JSON `500`.

### Run Tests Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
```

Optional coverage (standard library):

```bash
python -m trace --count --summary -m unittest discover -s tests -v
```

### Example Passing Output

```text
Ran 6 tests in 0.018s

OK
```

## Docker

How to use the containerized application (patterns):

- **Build image (local):** `docker build -t <local-name>:<tag> <path-to-app-python>`
- **Tag for Docker Hub:** `docker tag <local-name>:<tag> <username>/<repo>:<tag>`
- **Run container (local):** `docker run -p <host-port>:<container-port> --name <container-name> <image>`
- **Pull from Docker Hub:** `docker pull <username>/<repo>:<tag>`

Notes:
- The container exposes port `5002` by default (see `app.py`).
- The image runs as a non-root user for improved security.

## CI Workflow (GitHub Actions)

### Workflow Overview

Workflow file: `.github/workflows/python-ci.yml`

It runs on:
- `push` to `main` and `pull_request` into `main` for lint + tests.
- `push` of SemVer git tags (`vX.Y.Z`) for Docker build and push.

### Versioning Strategy

Chosen strategy: **Semantic Versioning (SemVer)**.

Why SemVer:
- Clear signal for breaking vs backward-compatible changes.
- Common convention for releases and container tags.

Docker tags produced on `vX.Y.Z`:
- `X.Y.Z` (full version)
- `X.Y` (rolling minor)
- `latest`

Example:
- `username/devops-info-service:1.2.3`
- `username/devops-info-service:1.2`
- `username/devops-info-service:latest`

### Secrets Required

Add these GitHub repository secrets:
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN` (Docker Hub access token)

### Release Flow

```bash
git tag v1.0.0
git push origin v1.0.0
```

The Docker job runs only on SemVer tags and pushes images with the tags above.
