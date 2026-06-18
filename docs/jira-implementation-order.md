# Jira Implementation Order

This execution order is based on technical dependencies, not only business grouping.

## Phase 1: Platform Foundation

Start here. Nothing else should move before these tasks are stable.

1. `T32` Align auth and user schemas with current contract
   Endpoint association: shared auth and user contracts used by `/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/password-recovery`, `/auth/password-reset`, `/users`, `/users/{user_id}`
2. `T34` Implement users and firms persistence model
   Endpoint association: foundational persistence for `/auth/register`, `/users`, `/users/{user_id}`
3. `T1` Implement auth API and JWT
   Endpoint association: `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`
4. `T31` Implement password recovery and reset endpoints
   Endpoint association: `POST /auth/password-recovery`, `POST /auth/password-reset`
5. `T3` Model users firms and access policies
   Endpoint association: cross-cutting authorization for `/users`, `/users/{user_id}`, `/cases`, `/cases/{id}`, `/cases/{id}/share`
6. `T33` Implement user CRUD API
   Endpoint association: `GET /users`, `POST /users`, `PATCH /users/{user_id}`, `DELETE /users/{user_id}`
7. `T2` Build Flutter auth shell and route guards
   Endpoint association: frontend integration for `POST /auth/login`, `POST /auth/refresh`
8. `T35` Build admin user management UI
   Endpoint association: frontend integration for `GET /users`, `POST /users`, `PATCH /users/{user_id}`, `DELETE /users/{user_id}`

Outcome:
- user contract stabilized
- auth flows working
- roles and firm boundaries enforced
- admin user management available

## Phase 2: Case Core

Cases depend on auth, ownership, and firm visibility already being solved.

1. `T5` Implement case CRUD API
   Endpoint association: `GET /cases`, `POST /cases`, `GET /cases/{id}`, `PATCH /cases/{id}`
2. `T6` Build case list detail and create screens
   Endpoint association: frontend integration for `GET /cases`, `POST /cases`, `GET /cases/{id}`
3. `T7` Implement case lifecycle transitions
   Endpoint association: primarily `PATCH /cases/{id}`
4. `T8` Build case status controls in UI
   Endpoint association: frontend integration for `PATCH /cases/{id}`
5. `T4` Implement case sharing API and audit logging
   Endpoint association: `POST /cases/{id}/share`, `GET /cases/{id}/share`

Outcome:
- cases can be created and managed
- lifecycle rules are enforced
- case collaboration is available

## Phase 3: Document Intake and Knowledge Pipeline

Do not start retrieval or analysis before document ingestion is reliable.

1. `T9` Implement document upload API and object storage integration
   Endpoint association: `POST /cases/{id}/documents`
2. `T11` Implement document versioning model
   Endpoint association: supports `POST /cases/{id}/documents`, `GET /cases/{id}/documents`
3. `T10` Build document upload and status UI
   Endpoint association: frontend integration for `POST /cases/{id}/documents`, `GET /cases/{id}/documents`
4. `T12` Implement OCR extraction worker
   Endpoint association: backend processing for document records exposed via `GET /cases/{id}/documents`
5. `T13` Implement text extraction quality scoring
   Endpoint association: backend status updates surfaced through `GET /cases/{id}/documents`
6. `T14` Implement chunking embeddings and pgvector indexing
   Endpoint association: supports downstream retrieval used by `/analyses` and `/chat`

Outcome:
- uploaded evidence is stored safely
- extraction pipeline works
- searchable case knowledge exists

## Phase 4: Legal Corpus and Retrieval

This phase enables verified AI.

1. `T15` Ingest legal corpus metadata and chunks
   Endpoint association: internal support for retrieval used by `/analyses` and `/chat`
2. `T16` Build retrieval orchestration and citation verifier
   Endpoint association: shared retrieval layer for `POST /cases/{id}/analyses` and `POST /chat/conversations/{id}/messages`

Outcome:
- legal sources are queryable
- verifier blocks unsupported citations

## Phase 5: Analysis

Only start after retrieval and verification are working.

1. `T17` Implement analysis generation API
   Endpoint association: `POST /cases/{id}/analyses`, `GET /cases/{id}/analyses/{analysis_id}`
2. `T18` Build analysis UI
   Endpoint association: frontend integration for `POST /cases/{id}/analyses`, `GET /cases/{id}/analyses/{analysis_id}`
3. `T19` Implement credit ledger and refund workflow
   Endpoint association: internal workflow tied to `POST /cases/{id}/analyses`

Outcome:
- structured legal analysis available
- failure and refund logic covered

## Phase 6: Chat

Chat should reuse the same verification guarantees as analysis.

1. `T20` Implement chat API and persistence
   Endpoint association: `POST /chat/conversations`, `GET /chat/conversations/{id}`, `POST /chat/conversations/{id}/messages`
2. `T21` Implement chat generation with verified citations
   Endpoint association: `POST /chat/conversations/{id}/messages`
3. `T22` Build legal chat UI
   Endpoint association: frontend integration for `POST /chat/conversations`, `GET /chat/conversations/{id}`, `POST /chat/conversations/{id}/messages`
4. `T23` Implement conversation-case linking rules
   Endpoint association: `POST /chat/conversations`, `PATCH /chat/conversations/{id}`

Outcome:
- legal chat is usable
- conversations can be attached to cases safely

## Phase 7: Drafting and Export

Drafting depends on completed analysis and validated legal context.

1. `T24` Implement tutela draft generation flow
   Endpoint association: `POST /cases/{id}/drafts/tutela`
2. `T26` Implement derecho de peticion generation flow
   Endpoint association: `POST /cases/{id}/drafts/derecho-de-peticion`
3. `T25` Build draft editor UI
   Endpoint association: frontend integration for `POST /cases/{id}/drafts/tutela`, `POST /cases/{id}/drafts/derecho-de-peticion`, `PATCH /drafts/{id}`
4. `T27` Implement export service
   Endpoint association: `POST /analyses/{id}/export`, `POST /drafts/{id}/export`

Outcome:
- editable legal drafts available
- outputs exportable in formal formats

## Phase 8: History and Release Hardening

Close with observability, history, and release confidence.

1. `T28` Implement history timeline aggregation API
   Endpoint association: `GET /cases/{id}/history`
2. `T29` Build history timeline UI
   Endpoint association: frontend integration for `GET /cases/{id}/history`
3. `T30` Create end-to-end regression suite and release checklist
   Endpoint association: cross-cutting validation for auth, users, cases, documents, analyses, chat, drafts, export, and history endpoints

Outcome:
- complete case traceability
- release validation in place

## Parallel Work Rules

Safe parallel tracks:

- `T2` can start once `T1` is stable enough for integration.
- `T35` can start once `T33` contract is stable.
- `T10` can proceed after `T9` endpoint contract is defined.
- `T18` can proceed after `T17` response shape is stable.
- `T22` can proceed after `T20` and `T21` contracts are stable.
- `T25` can proceed after draft generation contracts are stable.
- `T29` can proceed after `T28` returns stable event shapes.

Avoid parallelizing these too early:

- `T16` before `T14` and `T15`
- `T17` before `T16`
- `T21` before `T16`
- `T24` and `T26` before `T17`
- `T27` before `T17` and draft persistence

## Sprint Recommendation

### Sprint 1

- `T32`
- `T34`
- `T1`
- `T31`
- `T3`
- `T33`
- `T2`
- `T35`
- `T5`
- `T6`
- `T7`
- `T8`
- `T4`
- `T9`
- `T11`
- `T10`
- `T12`
- `T13`
- `T14`

Sprint 1 goal:
- secure access
- user admin
- case management
- document-to-knowledge pipeline

### Sprint 2

- `T15`
- `T16`
- `T17`
- `T18`
- `T19`
- `T20`
- `T21`
- `T22`
- `T23`
- `T24`
- `T26`
- `T25`
- `T27`
- `T28`
- `T29`
- `T30`

Sprint 2 goal:
- verified AI outputs
- drafting and export
- timeline and release readiness
