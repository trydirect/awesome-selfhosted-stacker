# Ombi API Endpoints

## REST API
- Base URL: `http://localhost:3579/api/v1`
- Auth: API key (Settings → Configuration → API Key)

## Key Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/Request/movie | List movie requests |
| POST | /api/v1/Request/movie | Create movie request |
| GET | /api/v1/Request/tv | List TV requests |
| POST | /api/v1/Request/tv | Create TV request |
| GET | /api/v1/Search/movie/{term} | Search movies |
| GET | /api/v1/Search/tv/{term} | Search TV shows |
| GET | /api/v1/Status | Application status |
