# Pleo Connector — Preparation

## Product Scope
Build a comprehensive Imperal connector for **Pleo** under category **C29. Expense Management & Corporate Cards**. The integration connects directly to the official **Pleo Open API v1** (`https://openapi.pleo.io/v1`), enabling full visibility and governance across corporate spend cards, out-of-pocket expenses, expense reports, spend policies, merchant categorization, employee reimbursements, and automated compliance auditing.

## Official API Specifications
- **API Architecture:** RESTful OpenAPI 3.0 specification
- **Base URL:** `https://openapi.pleo.io/v1`
- **Core Endpoints:**
  - `GET /me` — verify token privileges and company context
  - `GET /expenses` — list company expenses with cursor pagination
  - `GET /expenses/{id}` — detailed single expense record
  - `GET /cards` — smart physical and virtual corporate cards
  - `GET /reports` — aggregated expense reports and export batches
  - `GET /policies` — company spending limit and compliance policies
  - `GET /merchants` — merchant classifications
  - `GET /reimbursements` — employee pocket reimbursement records
- **Authentication Model:** Bearer Token via `Authorization: Bearer <api_key>`
- **Mandatory Requirements:**
  - Strict error classification: HTTP 429 rate limits with Retry-After extraction, HTTP 401/403 differentiation (Standard B8/B10).
  - Sanitization of Bearer tokens in error traces and diagnostic payloads (Standard B8).
  - Multi-tenant connection tracking and isolation via `connection_id` (Standard B9).

## Delivery Gates
1. [x] Official API discovery completed with Pleo Open API v1 specifications.
2. [x] Core resource endpoints and Bearer auth verified.
3. [x] Five mandatory specification documents authored.
4. [x] Client implemented with B8-B10 compliance, secret redaction, and 429/401 classification.
5. [x] Panel sidebar implemented conforming to UI_INTERFACE_STANDARD.md.
6. [x] Verification of functions, imports, and type hints passed.
7. [x] Deployment to Imperal platform completed.
8. [x] Pricing configured per PRICING_POLICY.md.
