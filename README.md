# LexIA MVP Workspace

This repository contains the implementation planning artifacts and starter structure for the `LexIA` MVP.

## Current Documents

- [Business Logic Source](./Logica_de_negocio_LexIA.docx)
- [MVP Implementation Plan](./docs/mvp-implementation-plan.md)
- [Jira Import CSV](./docs/jira-import.csv)
- [Mini Guía Jira ES](./docs/jira-mini-guia-es.md)
- [Team Delivery Plan](./docs/team-delivery-plan.md)

## Starter Structure

- `apps/frontend`
  Flutter Web client for case management, document handling, analysis, chat, drafting, and history.
- `services/api`
  FastAPI modular monolith for auth, cases, documents, analysis, chat, export, and audit.
- `services/ai-worker`
  Python worker for OCR, corpus ingestion, embeddings, retrieval, citation verification, and drafting.
- `packages/contracts`
  Shared API schemas, DTOs, and domain contracts.
- `infra/docker`
  Local development containers and compose files.
- `infra/sql`
  Database bootstrap scripts and migrations.

## MVP Priority

1. Auth and RBAC
2. Case CRUD and history
3. Document upload, OCR, and indexing
4. Verified RAG analysis
5. Verified legal chat
6. Draft generation and export

## Next Step

Use the CSV in `docs/jira-import.csv` to import or bulk-create the delivery backlog, then start implementation from the starter folders below.
