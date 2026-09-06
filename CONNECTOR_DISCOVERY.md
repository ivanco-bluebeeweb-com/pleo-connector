# Pleo Connector — Discovery & API Specifications

## Primary Source Documentation
- **Vendor:** Pleo Technologies
- **API Portal:** `https://developers.pleo.io`
- **Base URL:** `https://openapi.pleo.io/v1`
- **OpenAPI Schema Version:** OpenAPI 3.0

## Resource Mapping
- **Expenses:** `GET /expenses`, `GET /expenses/{id}`, `POST /expenses`, `PATCH /expenses/{id}`, `DELETE /expenses/{id}`
- **Cards:** `GET /cards`, `GET /cards/{id}`, `POST /cards`, `PATCH /cards/{id}`, `DELETE /cards/{id}`
- **Reports:** `GET /reports`, `GET /reports/{id}`, `POST /reports`, `PATCH /reports/{id}`, `DELETE /reports/{id}`
- **Policies:** `GET /policies`, `GET /policies/{id}`, `POST /policies`, `PATCH /policies/{id}`, `DELETE /policies/{id}`
- **Merchants:** `GET /merchants`, `GET /merchants/{id}`, `POST /merchants`, `PATCH /merchants/{id}`, `DELETE /merchants/{id}`
- **Reimbursements:** `GET /reimbursements`, `GET /reimbursements/{id}`, `POST /reimbursements`, `PATCH /reimbursements/{id}`, `DELETE /reimbursements/{id}`

## Multi-Tenancy & Error Classification
- Multi-account connections are isolated by unique `connection_id`.
- Rate limiting returns HTTP 429 and is parsed into `RATE_LIMITED` error codes with `Retry-After` delay tracking.
- Sensitive authentication tokens are strictly redacted before outputting to logs or error messages.
