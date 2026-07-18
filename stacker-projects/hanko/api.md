# Hanko API Endpoints

## REST API
- Base URL: `http://localhost:8000/v1`
- Auth: Bearer token (JWT)

## Key Endpoints
| Method | Path | Description |
|--------|------|-------------|
| POST | /v1/user | Create user |
| POST | /v1/login/initialize | Start login |
| POST | /v1/login/finalize | Complete login |
| POST | /v1/registration/initialize | Start registration |
| POST | /v1/registration/finalize | Complete registration |
| POST | /v1/webauthn/registration/initialize | Start passkey registration |
| POST | /v1/webauthn/login/initialize | Start passkey login |
| GET | /v1/users/{id} | Get user |
| PATCH | /v1/users/{id} | Update user |
