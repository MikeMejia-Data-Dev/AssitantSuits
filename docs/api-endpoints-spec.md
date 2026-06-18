# LexIA API Endpoint Specification

## Purpose

This document explains every MVP API endpoint defined in the implementation plan.

It is intended for:
- Backend implementation
- Frontend integration
- QA validation
- Product review

## Conventions

- Base path assumed: `/api/v1`
- Authentication: `Bearer access_token` unless the endpoint is explicitly public
- Content type: `application/json` unless the endpoint uses `multipart/form-data`
- All IDs are `UUID`
- All timestamps are `ISO 8601`

## Role Mapping

- `role_id = 1`: super admin
- `role_id = 2`: firm admin
- `role_id = 3`: lawyer or firm member

## Common Error Model

```json
{
  "error": {
    "code": "string",
    "message": "human readable message",
    "details": {}
  }
}
```

## Common Error Statuses

- `400` validation error
- `401` authentication required or invalid token
- `403` permission denied
- `404` resource not found
- `409` invalid state transition or business conflict
- `422` document quality insufficient
- `424` citation verification failed
- `500` internal technical failure

## Authentication Endpoints

### `POST /auth/register`

Creates a new user account.

- Auth: public
- Purpose: allow a lawyer or firm member to create credentials
- Request body:

```json
{
  "email": "user@example.com",
  "password": "StrongPassword123",
  "full_name": "Juan Perez",
  "professional_card": "1234567",
  "role_id": 2
}
```

- Success response `201`:

```json
{
  "user": {
    "user_id": "uuid",
    "email": "user@example.com",
    "full_name": "Juan Perez",
    "professional_card": "1234567",
    "role_id": 1,
    "firm_id": null,
    "status": true,
    "created_at": "2026-06-17T10:00:00Z"
  }
}
```

- Business rules:
- Email must be unique
- Password must meet minimum security requirements
- firm_id must be null at the begining
- `role_id` must be an integer between `1` and `3`
- `status` uses boolean semantics: `true` = active, `false` = inactive

### `POST /auth/login`

Authenticates a user and creates a session.

- Auth: public
- Purpose: issue access and refresh tokens
- Request body:

```json
{
  "email": "user@example.com",
  "password": "StrongPassword123"
}
```

- Success response `200`:

```json
{
  "access_token": "jwt",
  "refresh_token": "jwt",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "role_id": 1
  }
}
```

- Business rules:
- Only users with `status = true` can log in
- Failed attempts should be auditable
- `role_id` must be an integer between `1` and `3`

### `POST /auth/refresh`

Issues a new access token from a valid refresh token.

- Auth: public with refresh token
- Purpose: keep sessions active without forcing a new login
- Request body:

```json
{
  "refresh_token": "jwt"
}
```

- Success response `200`:

```json
{
  "access_token": "jwt",
  "token_type": "bearer",
  "expires_in": 3600
}
```

- Business rules:
- Refresh token must be valid, unexpired, and not revoked

### `POST /auth/password-recovery`

Starts the password recovery flow.

- Auth: public
- Purpose: generate a one-time recovery token for an existing account
- Request body:

```json
{
  "email": "user@example.com"
}
```

- Success response `200`:

```json
{
  "message": "If the email exists, a password recovery token has been generated."
}
```

- Business rules:
- Response must be identical whether the email exists or not
- Recovery token must expire
- Token delivery channel can be email or another verified out-of-band mechanism

### `POST /auth/password-reset`

Consumes a valid recovery token and updates the password.

- Auth: public
- Purpose: complete password recovery after token validation
- Request body:

```json
{
  "token": "recovery-token",
  "new_password": "StrongPassword123"
}
```

- Success response `200`:

```json
{
  "message": "Password updated successfully."
}
```

- Business rules:
- Token must be valid and unexpired
- Token must be single-use
- New password must meet minimum security requirements

## Super ADMIN

### `GET /users`

Lists the users visible to the current authenticated actor.

- Auth: required
- Purpose: support user administration, assignment flows, and internal directory lookup
- Query params:
- `status` optional boolean
- `role_id` optional integer between `1` and `3`
- `firm_id` optional
- `search` optional
- `page` optional
- `page_size` optional

- Success response `200`:

```json
{
  "items": [
    {
      "user_id": "uuid",
      "email": "user@example.com",
      "full_name": "Juan Perez",
      "professional_card": "1234567",
      "role_id": 2,
      "firm_id": null,
      "status": true,
      "created_at": "2026-06-17T10:00:00Z"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 1
}
```

- Business rules:
- `password_hash` must never be returned
- Visibility must respect tenant and firm boundaries
- `role_id` must be an integer between `1` and `3`
- `status` uses boolean semantics: `true` = active, `false` = inactive

### `POST /users`

Creates a new user.

- Auth: required
- Purpose: allow admin to create user accounts
- Request body:

```json
{
  "email": "user@example.com",
  "password": "StrongPassword123",
  "full_name": "Juan Perez",
  "professional_card": "1234567",
  "role_id": 1,
  "firm_id": null
}
```

- Success response `201`:

```json
{
  "user": {
    "user_id": "uuid",
    "email": "user@example.com",
    "full_name": "Juan Perez",
    "professional_card": "1234567",
    "role_id": 2,
    "firm_id": null,
    "status": true,
    "created_at": "2026-06-17T10:00:00Z"
  }
}
```

- Business rules:
- Email must be unique
- Password must meet minimum security requirements
- `password_hash` must be stored internally and never exposed
- `role_id` must be an integer between `1` and `3`
- `firm_id` may be null only for standalone users or platform-defined roles
- `status` uses boolean semantics: `true` = active, `false` = inactive

### `PATCH /users/{user_id}`

Updates editable fields of an existing user.

- Auth: required
- Purpose: allow profile maintenance and admin-driven user management
- Path params:
- `user_id` required
- Request body:

```json
{
  "full_name": "Juan David Perez",
  "professional_card": "7654321",
  "role_id": 2,
  "firm_id": "uuid",
  "status": true
}
```

- Success response `200`:

```json
{
  "user": {
    "user_id": "uuid",
    "email": "user@example.com",
    "full_name": "Juan David Perez",
    "professional_card": "7654321",
    "role_id": 2,
    "firm_id": "uuid",
    "status": true,
    "created_at": "2026-06-17T10:00:00Z"
  }
}
```

- Business rules:
- Only explicitly allowed fields may be updated
- Role, firm membership, and status changes should be restricted to authorized admins
- `role_id` must be an integer between `1` and `3`
- Password changes should use a dedicated auth flow, not this endpoint
- `status` uses boolean semantics: `true` = active, `false` = inactive

### `DELETE /users/{user_id}`

Deactivates a user account.

- Auth: required
- Purpose: remove a user from access without losing audit history
- Path params:
- `user_id` required

- Success response `200`:

```json
{
  "message": "User deactivated successfully."
}
```

- Business rules:
- Prefer soft delete or status change over physical deletion
- The last user with `status = true` and firm-admin privileges must not be removable if it would orphan the firm
- Existing sessions should be revoked after deactivation
- The action must be auditable

## Case Endpoints

### `GET /cases`

Lists the cases accessible to the current user.

- Auth: required
- Purpose: show the case inbox for an individual or firm member
- Query params:
- `status` optional
- `legal_area` optional
- `page` optional
- `page_size` optional

- Success response `200`:

```json
{
  "items": [
    {
      "case_id": "uuid",
      "name": "Despido Juan Perez",
      "description": "Despido injustifiado raro por x o y motivo",
      "legal_area": "Laboral",
      "status": true,
      "owner": {
        "user_id": "uuid",
        "firm_id": null
      },
      "created_at": "2026-06-17T10:00:00Z",
      "updated_at": "2026-06-17T10:00:00Z",
      "is_public":true
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 1
}
```

- Business rules:
- Results must include only owned or shared cases
- Cross-tenant leakage is forbidden
- status true = active, false = inactive

### `POST /cases`

Creates a new case.

- Auth: required
- Purpose: start a legal matter workspace
- Request body:

```json
{
  "name": "Despido Juan Perez",
  "legal_area": "Laboral",
  "description": "optional",
  "is_public": true
}
```

- Success response `201`:

```json
{
  "id": "uuid",
  "name": "Despido Juan Perez",
  "legal_area": "Laboral",
  "status": true,
  "owner": {
    "user_id": "uuid",
    "firm_id": null
  },
  "created_at": "2026-06-17T10:00:00Z"
}
```

- Business rules:
- `name` and `legal_area` are required
- Case ownership must be assigned at creation
- Case creation can be blocked by plan or case-limit rules

### `GET /cases/{id}`

Returns detailed information for a single case.

- Auth: required
- Purpose: load the main case detail view
- Path params:
- `id` required

- Success response `200`:

```json
{
  "id": "uuid",
  "name": "Despido Juan Perez",
  "legal_area": "Laboral",
  "status": true,
  "description": "optional",
  "owner": {
    "user_id": "uuid",
    "firm_id": null
  },
  "created_at": "2026-06-17T10:00:00Z",
  "updated_at": "2026-06-17T11:00:00Z",
}
```

- Business rules:
- User must be owner or shared member with access

### `PATCH /cases/{id}`

Updates editable fields of a case.

- Auth: required
- Purpose: rename or update metadata without recreating the case
- Request body example:

```json
{
  "name": "Despido Juan Perez v2",
  "description": "updated description",
  "legal_area": "Laboral",
  "status": true
}
```

- Success response `200`: updated case object

- Business rules:
- Illegal state changes must return `409`

## Document Endpoints

### `POST /cases/{id}/documents`

Uploads a document into a case.

- Auth: required
- Purpose: ingest legal evidence or working documents
- Content type: `multipart/form-data`
- Request fields:
- `file` required
- `case_id` optional if inferred from path

- Success response `202`:

```json
{
  "case_id": "uuid",
  "original_filename": "Caso de una ardillita",
  "file_type": "pdf",
  "file_size_bytes": 30,
  "created_at": "2026-06-17T10:00:00Z"
}
```

- Business rules:
- Supported types: `pdf`, `doc`, `docx`, `txt`
- Maximum file size is `20 MB`
- Password-protected files must be rejected
- Upload starts asynchronous OCR and extraction pipeline

### `GET /cases/{id}/documents`

Lists all documents attached to a case.

- Auth: required
- Purpose: show document inventory and processing states
- Success response `200`:

```json
{
  "items": [
    {
      "id": "uuid",
      "status": "vectorizado",
      "file_type": "pdf",
      "version_count": 1,
      "quality_score": 0.91
    }
  ]
}
```

- Business rules:
- Must respect case-level access control

### `GET /documents/{id}`

Returns the detail of a document.

- Auth: required
- Purpose: inspect one document and its current processing state
- Success response `200`:

```json
{
  "id": "uuid",
  "case_id": "uuid",
  "original_filename": "demanda.pdf",
  "status": "disponible_para_analisis",
  "file_type": "pdf",
  "version_count": 1,
  "quality_score": 0.91,
  "created_at": "2026-06-17T10:00:00Z"
}
```

- Business rules:
- Document access inherits from case access


## Analysis Endpoints

### `POST /cases/{id}/analysis`

Runs a legal analysis for a case.

- Auth: required
- Purpose: generate grounded legal analysis using case files plus legal corpus
- Request body:

```json
{
  "case_id": "uuid",
  "question": "optional focus",
  "force_refresh": false
}
```

- Success response `202`:

```json
{
  "id": "uuid",
  "status": "pending",
  "case_id": "uuid",
  "created_at": "2026-06-17T10:00:00Z"
}
```

- Business rules:
- Retrieval order is case knowledge first, corpus second
- Response must not be released without verified citations
- Required sections: summary, normative framework, jurisprudence, legal strategy, warnings and risks
- Minimum legal support: `3 normas + 2 sentencias`

### `GET /cases/{id}/analyses`

Lists analyses for a case.

- Auth: required
- Purpose: show analysis history and rerun candidates
- Success response `200`:

```json
{
  "items": [
    {
      "id": "uuid",
      "status": "completed",
      "corpus_version": "2026-Q2",
      "created_at": "2026-06-17T10:00:00Z"
    }
  ]
}
```

- Business rules:
- Results must stay scoped to the case

### `GET /analyses/{id}`

Returns a full analysis payload.

- Auth: required
- Purpose: render the detailed legal analysis screen
- Success response `200`:

```json
{
  "id": "uuid",
  "status": "completed",
  "sections": {
    "summary": "text",
    "normative_framework": "text",
    "jurisprudence": "text",
    "legal_strategy": "text",
    "warnings_risks": "text"
  },
  "citations": [
    {
      "source_id": "uuid",
      "source_type": "jurisprudence",
      "quoted_text": "text",
      "relevance_score": 0.97
    }
  ],
  "corpus_version": "2026-Q2",
  "disclaimer": "AI-assisted legal draft",
  "created_at": "2026-06-17T10:00:00Z"
}
```

- Business rules:
- If citation verification fails, return status reflecting failure and do not expose unverifiable content

## Chat Endpoints

### `POST /chat/conversations`

Creates a chat conversation.

- Auth: required
- Purpose: start a legal Q&A thread
- Request body example:

```json
{
  "title": "Consulta caso Juan Perez",
  "case_id": "uuid"
}
```

- Success response `201`:

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "case_id": "uuid",
  "title": "Consulta caso Juan Perez",
  "created_at": "2026-06-17T10:00:00Z"
}
```

- Business rules:
- Conversation can be case-linked or generic
- Generic chat still must enforce tenant boundaries

### `POST /chat/conversations/{id}/messages`

Sends a message and generates a cited answer.

- Auth: required
- Purpose: ask a legal question and receive grounded output
- Request body:

```json
{
  "content": "Que riesgos procesales ves en este caso?",
  "case_id": "uuid"
}
```

- Success response `200`:

```json
{
  "message_id": "uuid",
  "answer": "text",
  "citations": [
    {
      "source_id": "uuid",
      "source_type": "norma",
      "quoted_text": "text",
      "relevance_score": 0.94
    }
  ],
  "linked_case_id": "uuid"
}
```

- Business rules:
- Content length must stay within configured bounds
- Citation verification is mandatory before answer release
- Chat must not mutate case facts automatically

### `GET /chat/conversations/{id}`

Returns a conversation with all messages.

- Auth: required
- Purpose: reload an existing thread
- Success response `200`:

```json
{
  "id": "uuid",
  "title": "Consulta caso Juan Perez",
  "case_id": "uuid",
  "messages": [
    {
      "id": "uuid",
      "role": "user",
      "content": "question",
      "created_at": "2026-06-17T10:00:00Z"
    },
    {
      "id": "uuid",
      "role": "assistant",
      "content": "answer",
      "citations": [],
      "created_at": "2026-06-17T10:00:05Z"
    }
  ]
}
```

- Business rules:
- Only the conversation owner or authorized shared participants may read it

## Drafting Endpoints

### `POST /cases/{id}/drafts/tutela`

Generates a tutela draft.

- Auth: required
- Purpose: produce an editable first draft grounded on case evidence and analysis
- Request body:

```json
{
  "analysis_id": "uuid",
  "custom_instructions": "Enfatizar afectacion al minimo vital"
}
```

- Success response `202`:

```json
{
  "id": "uuid",
  "type": "tutela",
  "status": "draft"
}
```

- Business rules:
- Must be based on existing case context
- Output is editable draft, not final signed filing

### `POST /cases/{id}/drafts/derecho-peticion`

Generates a derecho de peticion draft.

- Auth: required
- Purpose: produce a first draft for petition workflows
- Request body:

```json
{
  "analysis_id": "uuid",
  "custom_instructions": "Solicitar respuesta en termino legal"
}
```

- Success response `202`:

```json
{
  "id": "uuid",
  "type": "derecho_peticion",
  "status": "draft"
}
```

- Business rules:
- Same grounding and editability requirements as tutela drafts

### `PATCH /generated-documents/{id}`

Updates a generated draft.

- Auth: required
- Purpose: allow lawyer editing before export
- Request body example:

```json
{
  "content_markdown": "# Nuevo contenido\n\nTexto editado por abogado."
}
```

- Success response `200`:

```json
{
  "id": "uuid",
  "status": "edited",
  "content": "# Nuevo contenido\n\nTexto editado por abogado."
}
```

- Business rules:
- Manual edits must be preserved
- Editing should not overwrite source analysis history

### `POST /generated-documents/{id}/export`

Exports a generated draft.

- Auth: required
- Purpose: produce final downloadable outputs
- Request body example:

```json
{
  "formats": ["pdf", "docx"]
}
```

- Success response `200`:

```json
{
  "id": "uuid",
  "type": "tutela",
  "status": "exported",
  "export_urls": {
    "pdf": "signed-url",
    "docx": "signed-url"
  }
}
```

- Business rules:
- Only authorized users may export
- Export events must be logged

## Access And History Endpoints

### `POST /cases/{id}/share`

Shares a case with another user.

- Auth: required
- Purpose: controlled collaboration inside a firm
- Request body:

```json
{
  "granted_to_user_id": "uuid",
  "permission": "read"
}
```

- Success response `201`:

```json
{
  "id": "uuid",
  "case_id": "uuid",
  "granted_to_user_id": "uuid",
  "permission": "read",
  "granted_by_user_id": "uuid",
  "created_at": "2026-06-17T10:00:00Z"
}
```

- Business rules:
- Only firm admin or authorized owner can share
- Permission values allowed: `read`, `read_write`
- Sharing must generate audit events

### `GET /cases/{id}/access`

Lists current access grants for a case.

- Auth: required
- Purpose: review collaboration permissions
- Success response `200`:

```json
{
  "items": [
    {
      "user_id": "uuid",
      "permission": "read_write",
      "granted_by_user_id": "uuid",
      "created_at": "2026-06-17T10:00:00Z"
    }
  ]
}
```

- Business rules:
- Visibility of ACL data should be limited to authorized managers and owners

### `GET /cases/{id}/history`

Returns the audit history of a case.

- Auth: required
- Purpose: trace who did what and when
- Success response `200`:

```json
{
  "items": [
    {
      "id": "uuid",
      "actor_user_id": "uuid",
      "action": "document_uploaded",
      "target_type": "document",
      "target_id": "uuid",
      "metadata": {},
      "created_at": "2026-06-17T10:00:00Z"
    }
  ]
}
```

- Business rules:
- History must include sharing, uploads, analysis runs, exports, and lifecycle changes
- Audit records must be immutable

## Implementation Notes

- Endpoints that trigger heavy processing should return `202 Accepted` and execute work asynchronously.
- ACL checks must be enforced in every case-scoped, document-scoped, analysis-scoped, chat-scoped, and export-scoped endpoint.
- AI-generated outputs must never bypass retrieval and citation verification.
- Response contracts should be reflected in the FastAPI OpenAPI schema and used by frontend typed clients.
