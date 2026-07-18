# Jellyseerr API Endpoints

## REST API
- Base URL: `http://localhost:5055/api/v1`
- Auth: API key (Settings → General → API Key)

## Key Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/status | Application status |
| GET | /api/v1/auth/me | Current user |
| GET | /api/v1/request | List requests |
| POST | /api/v1/request | Create request |
| GET | /api/v1/search | Search for media |
| GET | /api/v1/movie/{id} | Movie details |
| GET | /api/v1/tv/{id} | TV show details |
