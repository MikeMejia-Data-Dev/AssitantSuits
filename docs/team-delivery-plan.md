# LexIA Team Delivery Plan

## Ownership by Role

### Flutter Developer 1
- Authentication shell, route guards, and session persistence.
- Case list, case detail, case creation, and lifecycle controls.
- History timeline UI and shared-case visibility.

### Flutter Developer 2
- Document upload and processing-status UI.
- Analysis request and result screens.
- Legal chat UI.
- Draft editor and export actions.

### Backend Developer
- FastAPI modular monolith foundation.
- Auth, RBAC, firm membership, ACL enforcement.
- Case CRUD, lifecycle, sharing, history, export, and credit-ledger APIs.
- Storage integration, data model, and audit events.

### AI Engineer
- OCR and extraction pipeline.
- Chunking, embeddings, vector indexing, and legal corpus ingestion.
- Retrieval orchestration, citation verification, analysis generation, chat generation.
- Tutela and derecho de peticion generation flows.

### QA Engineer
- Acceptance criteria traceability.
- Test data and end-to-end regression coverage.
- ACL and security matrix validation.
- Release readiness and pilot go-live checklist.

## Sprint Assignment

### Sprint 1
- Flutter Developer 1: `T2`, `T6`, `T8`
- Flutter Developer 2: `T10`
- Backend Developer: `T1`, `T3`, `T4`, `T5`, `T7`, `T9`, `T11`
- AI Engineer: `T12`, `T13`, `T14`
- QA Engineer: test planning on `S1-S6`, fixtures for upload and role access

### Sprint 2
- Flutter Developer 1: `T29`
- Flutter Developer 2: `T18`, `T22`, `T25`
- Backend Developer: `T17`, `T19`, `T20`, `T23`, `T27`, `T28`
- AI Engineer: `T15`, `T16`, `T21`, `T24`, `T26`
- QA Engineer: `T30`

## Delivery Notes

- The backend and AI engineer are on the critical path; any blockage on `T12-T17` threatens the MVP.
- Flutter work is intentionally split by workflow to minimize merge conflicts.
- QA must start in Sprint 1 with fixtures and role/access matrices, not only at the end.
- Billing and self-serve plan management remain out of scope for the 2-week MVP.
