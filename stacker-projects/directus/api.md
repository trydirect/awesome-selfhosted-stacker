# Directus API Endpoints

## REST API
- Base URL: `http://localhost:8055/items`
- Auth: Bearer token (login at `/auth/login`)

## GraphQL
- URL: `http://localhost:8055/graphql`
- Auth: Bearer token

## Key Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | /items/{collection} | List items in collection |
| POST | /items/{collection} | Create item |
| GET | /items/{collection}/{id} | Get item by ID |
| PATCH | /items/{collection}/{id} | Update item |
| DELETE | /items/{collection}/{id} | Delete item |
| GET | /collections | List collections |
| GET | /fields/{collection} | List fields |
| POST | /auth/login | Login |
| GET | /users/me | Current user |

## Endpoint Specs (for `stacker pipe create`)
| Method | Path | Fields |
|--------|------|--------|
| POST | /items | name,email,message |
| GET | /items | — |
| POST | /auth/login | email,password |

## OpenAPI Spec
- URL: `http://localhost:8055/server/specs/oas`
