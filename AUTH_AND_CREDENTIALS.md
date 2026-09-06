# Pleo Connector — Authentication & Credentials Standard

## Overview
Complies with `AUTH_AND_CREDENTIALS_STANDARD.md` (Standards B1 through B10).

## Credential Requirements
- **Auth Type:** API Key / Bearer Token
- **Header Format:** `Authorization: Bearer <api_key>`
- **Token Scope:** Pleo developer portal personal or organization API token with expense read/write permissions.

## Security Controls
- **B8 Redaction:** Tokens are masked (`_mask(value)`) in all listings and sanitized in exceptions.
- **B9 Multi-Account:** All calls accept optional `connection_id` targeting explicit tenant configurations.
- **B10 Error Classification:** Native handling of 401 Unauthorized, 403 Forbidden, and 429 Rate Limited responses.
