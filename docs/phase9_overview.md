# Phase 9 Overview

Phase 9 adds production-oriented hardening around the local application.

## Included

- Request IDs, status codes, and duration logging through FastAPI middleware
- `/health` for process health and `/ready` for Ollama/Chroma dependency readiness
- Configurable upload-size limit via `MAX_UPLOAD_MB`
- Docker health checks and dependency ordering
- `.dockerignore` to keep local environments, tests, and data out of the image build context
- GitHub Actions CI running the test suite on Python 3.11

## Health Semantics

`/health` answers whether the API process is responding. It does not initialize Ollama or Chroma and should remain useful for a basic liveness probe. `/ready` checks that the Chroma directory exists and Ollama's `/api/tags` endpoint responds, so it is appropriate for routing traffic only when dependencies are available.

## Honest Simplification

This is baseline hardening, not a complete production platform. It does not provide authentication, rate limiting, centralized logs, secrets management, TLS termination, autoscaling, distributed tracing, or a job queue. CI also runs tests only; a larger deployment would add image scanning, dependency auditing, integration tests, and deployment promotion gates.
