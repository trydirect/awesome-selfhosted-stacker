# Infisical API Endpoints

## REST API
- Base URL: `http://localhost:8080/api/v1`
- Auth: Service token or universal auth (client ID + client secret)

## Key Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/secrets | List secrets |
| POST | /api/v1/secrets/{secretName} | Create secret |
| PATCH | /api/v1/secrets/{secretName} | Update secret |
| DELETE | /api/v1/secrets/{secretName} | Delete secret |
| GET | /api/v1/workspaces | List workspaces |
| GET | /api/v1/workspace/{id}/environments | List environments |

## SDKs
- Node: `npm install @infisical/sdk`
- Python: `pip install infisical-python`
- Go: `go get github.com/infisical/infisical-sdk-go`
