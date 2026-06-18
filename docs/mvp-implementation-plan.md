# LexIA MVP Implementation Plan

## Product Analysis

### Product Vision
`LexIA` is a Colombian legal-assistance platform that turns unstructured case documents into verified, reusable legal knowledge per `Expediente Juridico`, then uses that knowledge to produce grounded analysis, chat responses, and first-draft legal documents.

### Problem Statement
Lawyers and firms lose time organizing case files, extracting facts from documents, locating applicable norms and jurisprudence, and drafting repetitive legal outputs. The business document defines the value as transforming unstructured legal documents into analyzable, reusable legal information.

### Target Users
- `Abogado individual`
- `Administrador de Firma`
- `Miembro de Firma`

### Business Goals
- Centralize case files and legal documents.
- Produce legally grounded AI analysis and chat.
- Preserve case knowledge and history.
- Enable first-draft generation of `tutelas` and `derechos de peticion`.
- Support controlled collaboration inside firms.

### Success Metrics
- Time from case creation to first AI analysis `< 15 min`.
- `>= 90%` of uploaded supported documents processed successfully.
- `100%` of AI outputs include verified citations.
- `0` cross-case knowledge leakage.
- `>= 70%` of pilot users complete one end-to-end flow: create case -> upload docs -> run analysis -> export result.

### Core Features
- Case creation and lifecycle management.
- Document upload, versioning, OCR/text extraction, vectorization.
- Per-case knowledge base with strict isolation.
- Verified RAG analysis.
- Verified legal chat.
- History and audit trail.
- Draft generation for `tutelas` and `derechos de peticion`.
- Basic sharing and permissions for firms.
- PDF and DOCX export.

## Requirements Analysis

### Functional Requirements
- Create, update, list, close, archive `expedientes` with owner, name, and legal area (`RN-001` to `RN-005`, `RN-043`).
- Upload `PDF/DOC/DOCX/TXT` up to `20 MB`, reject unsupported/password-protected files, keep non-destructive versions (`RN-006` to `RN-010`).
- Process documents through states `Cargado -> Procesando -> Texto extraido -> Vectorizado -> Disponible para analisis | Calidad insuficiente` (`RN-011` to `RN-013`).
- Build per-case embeddings and search case content before national corpus (`RN-014`, `RN-015`).
- Generate grounded AI responses only from retrieved evidence; reject unverifiable citations (`RN-016` to `RN-018`).
- Produce analysis with required sections and minimum sources `3 normas + 2 sentencias` (`RN-019`, `RN-021`).
- Store chat and analysis history; optionally link chat to case without auto-mutating case data (`RN-022` to `RN-029`).
- Generate editable `tutelas` and `derechos de peticion` with required content (`RN-030` to `RN-034`).
- Share cases only through firm admin with `read` or `read_write` permissions and audit logs (`RN-035` to `RN-042`, `RN-049`, `RN-052`).

### Non-Functional Requirements
- Strong tenant and case isolation.
- Full auditability of shared access and AI outputs.
- Asynchronous processing for upload, OCR, embedding, and analysis.
- Citation verification before response release.
- Secure storage and encrypted transport.
- Responsive UI optimized for desktop-first legal work.
- Recoverable failures and idempotent processing jobs.
- Compliance-oriented handling of Colombian personal data (`RN-051`).

### Business Rules
- Source of truth is `RN-001` to `RN-052`.
- Most critical rules for MVP: `RN-005`, `RN-011`, `RN-015` to `RN-018`, `RN-019`, `RN-023`, `RN-025`, `RN-035` to `RN-042`, `RN-049` to `RN-052`.
- Central business rule: no AI output may be generated solely from the LLM without RAG and specialized corpus.

### Assumptions
- Because plans and credits are not fully defined (`RN-044` to `RN-048`), MVP uses admin-configured limits and a simple internal credit ledger behind feature flags, not self-serve billing.
- MVP targets responsive `Flutter Web` first; mobile packaging is optional after validation.
- National legal corpus is preloaded or offline-ingested before pilot launch.
- Document generation outputs editable drafts, not final signed legal filings.

### Dependencies
- Reliable Colombian legal corpus for norms and jurisprudence.
- OCR engine for scanned PDFs and images.
- LLM and embedding provider with enterprise data controls.
- Object storage, relational DB, vector search, and job queue.
- Legal disclaimer text approved by product and legal stakeholders.

### Constraints
- Delivery window: `2 weeks`.
- Team: `2 Flutter`, `1 Backend`, `1 AI`, `1 QA`.
- MVP only; no complex billing, analytics, or advanced reporting.
- No invented business rules beyond explicit assumptions.

## Domain Modeling

### Aggregate Roots
- `CaseFile (Expediente)`
- `UserAccount`
- `Firm`
- `Document`
- `Analysis`
- `Conversation`
- `GeneratedLegalDocument`

### Entities
- `CaseFile`: owner, legal_area, status, timestamps.
- `Document`: metadata, current_status, source_type, password_protected_flag.
- `DocumentVersion`: file_path, checksum, uploaded_by, version_number.
- `KnowledgeChunk`: chunk_text, embedding_ref, source_span, corpus_type.
- `Analysis`: sections, corpus_version, disclaimer, status, credit_event_id.
- `Conversation`: linked_case_id nullable.
- `ChatMessage`: role, prompt, response, citations.
- `GeneratedLegalDocument`: type `tutela|derecho_peticion`, editable_content.
- `AccessGrant`: case_id, grantee_user_id, permission.
- `AuditEvent`: actor, action, target_type, target_id.
- `PlanProfile` and `CreditLedger` as configurable support entities.

### Value Objects
- `CaseStatus`
- `DocumentStatus`
- `PermissionType`
- `Citation`
- `LegalArea`
- `FileMetadata`
- `SourceReference`
- `CorpusVersion`

### Relationships
- One `UserAccount` or `Firm` owns many `CaseFiles`.
- One `CaseFile` has many `Documents`, `Analyses`, `Conversations`, `GeneratedLegalDocuments`, `AuditEvents`, `AccessGrants`.
- One `Document` has many `DocumentVersions` and many `KnowledgeChunks`.
- `Analysis` references many verified `Citations`.
- `Conversation` has many `ChatMessages`.

### State Transitions
- `CaseFile`: `Pendiente de analisis -> En proceso -> En espera -> Cerrado -> Archivado`; reopening from `En espera` or `Archivado` allowed by owner/admin assumption, but close/archive never deletes knowledge (`RN-043`).
- `Document`: `Cargado -> Procesando -> Texto extraido -> Vectorizado -> Disponible para analisis` or `Calidad insuficiente`.
- `Analysis`: `pending -> running -> completed | failed_refunded`.
- `GeneratedLegalDocument`: `draft -> edited -> exported`.

## Architecture

### Frontend Architecture
- `Flutter Web` with feature modules: Auth, Cases, Documents, Analysis, Chat, Drafting, Firm Sharing, History.
- `Riverpod` for state management: simple, testable, strong async handling, good for a small Flutter team.
- Desktop-first responsive layout because legal users work with dense content and documents.
- Rich text editor for editable drafts.

### Backend Architecture
- `FastAPI` modular monolith.
- Justification: fastest path for one backend dev, strong Python ecosystem, easy AI integration, async APIs, and OpenAPI generation.
- Modules: auth/rbac, cases, documents, knowledge, analysis, chat, drafting, export, audit, plans.
- Background workers for OCR, parsing, embeddings, retrieval prep, and long-running analysis jobs.

### AI Architecture
- Separate Python worker service sharing domain contracts with backend.
- Justification: isolates AI dependencies and long-running tasks from request API; fits one AI engineer while keeping the deployment simple.

### Infrastructure Architecture
- `PostgreSQL + pgvector`: one database for transactional and vector search, fastest MVP choice.
- `Redis`: job queue and status cache.
- `S3-compatible object storage`: document versions and exports.
- `Docker Compose` for local dev; `Cloud Run` or `Render` for API and worker; managed Postgres and object storage for production.
- Justification: managed services reduce ops overhead inside a 2-week window.

### Legal Corpus Storage Strategy
- For scraped legal corpus, use a hybrid model instead of choosing only relational or only non-relational storage.
- Keep raw scraped artifacts in `S3-compatible object storage` as a lightweight `data lake` layer: original HTML, PDF, JSON extraction results, OCR outputs, parsing logs, and reprocessing snapshots.
- Keep normalized operational metadata, citation registry, ingestion status, and traceability in `PostgreSQL`.
- Keep vectorized retrieval data in `pgvector` so corpus search and transactional consistency remain in the same operational database for MVP.
- Justification: legal scraping produces heterogeneous, evolving, and reprocessable raw inputs, while the product also requires strict referential integrity, citation verification, and auditable lineage.
- Decision: for MVP, do not introduce a separate document database; `JSONB` columns plus object storage cover variable scraper payloads with lower operational complexity.
- Scaling path: if corpus volume grows enough to make reprocessing, analytics, or batch enrichment expensive in the MVP stack, evolve the object storage layer into a formal `data lake/lakehouse` before adding a separate NoSQL database.

### Security Architecture
- JWT-based auth with refresh tokens.
- RBAC plus per-case ACL enforcement on every read and write path.
- Object storage private buckets only; signed URLs for controlled download.
- Encryption in transit and at rest.
- Audit logging for share, access, and export actions.
- Prompt-context filters to prevent cross-case retrieval.
- No training on customer data (`RN-009`, `RN-050`).

## Database Design

### Recommended Persistence Model For Scraped Legal Data
- `Relational core`: best fit for `cases`, `users`, `documents`, `analyses`, `citations`, corpus source registry, ingestion jobs, and audit events because those domains need constraints, joins, lineage, and verifiable references.
- `Non-relational/raw layer`: useful for unstructured scraper outputs, parser payloads, OCR responses, and intermediate enrichment artifacts, but better stored in object storage than in a standalone NoSQL engine during MVP.
- `Why not fully NoSQL`: the legal product depends on exact source resolution, corpus versioning, deduplication, and citation verification; those requirements are easier and safer to enforce in a relational model.
- `Why not relational only`: storing every raw scrape artifact inside operational tables would increase storage cost, schema churn, and reprocessing friction.
- Final recommendation: use `PostgreSQL` as the primary database, `pgvector` for semantic retrieval, and object storage as the raw corpus lake. Add a dedicated NoSQL database only if future scraper throughput or enrichment workloads clearly exceed what `PostgreSQL + JSONB + object storage` can support.

### Tables, Columns, Relationships, Constraints, Indexes

#### `users`
- Columns: `user_id`,`full_name`,`professional_card`, `email unique`, `password_hash`, `role`, `firm_id null`, `status`, `created_at`
- Relationships: many-to-one with `firms`
- Indexes: `email unique`, `(firm_id, role)`

#### `firms`
- Columns: `firm_id`, `name`, `created_at`, `user_id`
- Relationships: one-to-many with `users`, optional ownership relation with `cases`
- Indexes: `name`

#### `cases`
- Columns: `case_id`, `user_id`, `firm_id null`, `name`, `legal_area`, `status`, `description null`, `created_at`, `updated_at`, `is_public`
- Constraints: `name` and `legal_area` not null (`RN-002`)
- Relationships: one-to-many with `documents`, `analyses`, `conversations`, `generated_documents`, `audit_events`, `case_access`
- Indexes: `(user_id, status)`, `(firm_id, status)`

#### `documents`
- Columns: `doc_id`, `case_id`, `original_filename`, `file_type`, `file_size_bytes`,  `created_at`
- Constraints: `file_type` limited to `pdf|doc|docx|txt` (`RN-006`)
- Relationships: one-to-many with `document_versions`, `knowledge_chunks`
- Indexes: `(case_id, status)`

#### `knowledge_chunks`
- Columns: `id`, `case_id`, `document_id`, `document_version_id`, `chunk_index`, `chunk_text`, `embedding vector`, `source_page null`, `source_span_start null`, `source_span_end null`, `created_at`
- Relationships: many-to-one with `cases`, `documents`, `document_versions`
- Indexes: `(case_id, document_id)`, `ivfflat (embedding vector_cosine_ops)`

#### `legal_corpus_sources`
- Columns: `id`, `source_type`, `title`, `citation_text`, `jurisdiction`, `external_ref`, `publication_date`, `corpus_version`, `storage_key`, `is_active`
- Optional columns for scraping pipeline: `source_url`, `content_hash`, `scraped_at`, `parser_version`, `raw_payload_jsonb`
- Indexes: `(source_type, corpus_version)`, `(external_ref)`

#### `legal_corpus_chunks`
- Columns: `id`, `source_id`, `chunk_index`, `chunk_text`, `embedding vector`, `created_at`
- Relationships: many-to-one with `legal_corpus_sources`
- Indexes: `(source_id, chunk_index)`, `ivfflat (embedding vector_cosine_ops)`

#### `corpus_ingestion_runs`
- Columns: `id`, `source_id`, `status`, `scraper_name`, `started_at`, `finished_at null`, `raw_storage_key`, `normalized_storage_key null`, `error_message null`, `stats_jsonb`
- Relationships: many-to-one with `legal_corpus_sources`
- Indexes: `(source_id, started_at desc)`, `(status, started_at desc)`

#### `analyses`
- Columns: `id`, `case_id`, `status`, `summary`, `normative_framework`, `jurisprudence`, `legal_strategy`, `warnings_risks`, `corpus_version`, `disclaimer_text`, `created_by_user_id`, `credit_ledger_id null`, `created_at`, `completed_at null`, `failure_reason null`
- Constraints: analysis cannot be `completed` without citations and disclaimer
- Indexes: `(case_id, created_at desc)`

#### `analysis_citations`
- Columns: `id`, `analysis_id`, `source_id`, `source_type`, `quoted_text`, `relevance_score`
- Relationships: many-to-one with `analyses`, `legal_corpus_sources`
- Indexes: `(analysis_id)`, `(source_id)`

#### `conversations`
- Columns: `id`, `user_id`, `case_id null`, `title`, `created_at`
- Relationships: many-to-one with `users`, optional many-to-one with `cases`
- Indexes: `(case_id, created_at desc)`, `(user_id, created_at desc)`

#### `chat_messages`
- Columns: `id`, `conversation_id`, `role`, `content`, `response_status`, `created_at`
- Relationships: many-to-one with `conversations`
- Indexes: `(conversation_id, created_at)`

#### `chat_citations`
- Columns: `id`, `chat_message_id`, `source_id`, `source_type`, `quoted_text`, `relevance_score`
- Relationships: many-to-one with `chat_messages`, `legal_corpus_sources`
- Indexes: `(chat_message_id)`, `(source_id)`

#### `generated_documents`
- Columns: `id`, `case_id`, `analysis_id null`, `type`, `status`, `content_markdown`, `content_docx_key null`, `content_pdf_key null`, `created_by_user_id`, `created_at`
- Relationships: many-to-one with `cases`, optional many-to-one with `analyses`
- Indexes: `(case_id, type, created_at desc)`

#### `audit_events`
- Columns: `id`, `actor_user_id`, `action`, `target_type`, `target_id`, `metadata_json`, `created_at`
- Indexes: `(target_type, target_id, created_at desc)`, `(actor_user_id, created_at desc)`

#### `plan_profiles`
- Columns: `id`, `name`, `active_case_limit null`, `features_json`, `is_default`
- Indexes: `name unique`

#### `credit_ledger`
- Columns: `id`, `user_id`, `operation_type`, `delta`, `status`, `related_resource_type`, `related_resource_id`, `created_at`
- Indexes: `(user_id, created_at desc)`, `(related_resource_type, related_resource_id)`



### Relational Entity Model

![Relational Entity Model](<./WhatsApp Image 2026-06-17 at 18.45.40.jpeg>)




## API Design

### REST Endpoints

#### Auth
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/password-recovery`
- `POST /auth/password-reset`

#### superadmin view

- `GET /users`
- `POST /users`
- `PATCH /users`
- `DELETE /users`

#### users view

- `GET /cases`
- `POST /cases`
- `GET /cases/{id}`
- `PATCH /cases/{id}`

- `POST /cases/{id}/documents`
- `GET /cases/{id}/documents`
- `GET /documents/{id}`

## Analysis Endpoints
- `POST /cases/{id}/analysis`
- `GET /cases/{id}/analyses`
- `GET /analyses/{id}`
- `POST /chat/conversations`
- `POST /chat/conversations/{id}/messages`
- `GET /chat/conversations/{id}`
- `POST /cases/{id}/drafts/tutela`
- `POST /cases/{id}/drafts/derecho-peticion`
- `PATCH /generated-documents/{id}`
- `POST /generated-documents/{id}/export`
- `POST /cases/{id}/share`
- `GET /cases/{id}/access`
- `GET /cases/{id}/history`


### Error Responses
- `400` validation error: unsupported format, size limit, question length, missing required fields.
- `403` access denied: role or permission mismatch.
- `409` case limit reached, invalid state transition.
- `422` document quality insufficient for analysis.
- `424` citation verification failed; response withheld per `RN-017` and `RN-018`.
- `500` technical failure with credit refund event where applicable (`RN-020`, `RN-048`).

## AI Design

### RAG Architecture
- Step 1: retrieve top case chunks from `knowledge_chunks`.
- Step 2: retrieve top national corpus chunks from `legal_corpus_chunks`.
- Step 3: assemble grounded context with chunk metadata and corpus IDs.
- Step 4: LLM generates structured output constrained to citations from retrieved set only.
- Step 5: verifier cross-checks every cited source against corpus before release.

### OCR Pipeline
- File classifier -> text extraction (`pdfplumber`, `python-docx`, TXT parser) -> OCR fallback (`OCRmyPDF/Tesseract`) for scanned PDFs and images -> quality scoring -> chunking -> embedding -> ready.
- If extraction quality is insufficient, set `Calidad insuficiente` (`RN-013`).

### Embedding Strategy
- One Spanish-capable legal-semantic embedding model for both case docs and legal corpus.
- Chunk size `500-800` tokens with overlap `80-120`; store page and span metadata for traceability.

### Retrieval Strategy
- Hybrid retrieval: vector similarity + metadata filtering by `case_id` or `source_type`.
- Order enforced: case knowledge first, national corpus second (`RN-015`).
- MMR or reranking to diversify norms and jurisprudence.
- Analysis gate requires at least `3` normative and `2` jurisprudential verified sources (`RN-019`).

### Citation Verification Strategy
- Every generated citation must map to `legal_corpus_sources.id` or stored case document span.
- If a citation string cannot be resolved to a real corpus entry, discard and regenerate; if still unresolved, block release (`RN-017`, `RN-018`).

### Hallucination Prevention Strategy
- No free-form answer without retrieved context.
- Prompt instructs model to say evidence is insufficient when support is missing.
- Structured JSON output with citations array only from provided source IDs.
- Post-generation validator enforces minimum source counts, disclaimer, and citation existence.
- Human-editable outputs only; AI never auto-modifies case facts (`RN-025`, `RN-032`).

## MVP Definition

### Must Have Features
- Auth, roles, firm membership, RBAC.
- Case CRUD and lifecycle.
- Document upload, versioning, processing with OCR.
- Per-case knowledge base and strict isolation.
- Verified analysis generation.
- Verified legal chat.
- History storage.
- Editable `tutela` and `derecho de peticion` drafts.
- PDF and DOCX export.
- Sharing with audit trail.

### Should Have Features
- Simple credit ledger and refund handling.
- Corpus version display and analysis traceability.
- Reprocess failed documents.
- Basic dashboard with processing and analysis statuses.

### Deferred Features
- Self-serve billing and final plan catalog.
- Advanced analytics and reporting.
- Multi-workspace admin tooling.
- Portability and deletion workflows once data policy is defined.
- Complex collaboration workflows beyond explicit sharing.
- Mobile-native optimizations if web validates value first.

## Jira Backlog

### Epics
1. `E1 Auth, Roles, Firm Access`
   Business Goal: secure access control.
   Description: authentication, role enforcement, firm membership, case sharing foundations.
   Dependencies: none.
   Story Points: `13`.
2. `E2 Case & History Management`
   Business Goal: create and manage `expedientes`.
   Description: case lifecycle, ownership, timeline, and history preservation.
   Dependencies: `E1`.
   Story Points: `13`.
3. `E3 Document Intake & Knowledge Base`
   Business Goal: ingest and process docs into case knowledge.
   Description: upload, versioning, OCR, extraction, chunking, embeddings, case isolation.
   Dependencies: `E2`.
   Story Points: `21`.
4. `E4 Verified RAG Analysis & Chat`
   Business Goal: grounded AI outputs with citations.
   Description: retrieval, verifier, analysis generation, legal chat.
   Dependencies: `E3`.
   Story Points: `21`.
5. `E5 Drafting & Export`
   Business Goal: produce editable legal drafts and exports.
   Description: `tutela`, `derecho de peticion`, export to PDF and DOCX.
   Dependencies: `E4`.
   Story Points: `13`.
6. `E6 QA, Audit, Release Readiness`
   Business Goal: compliance, tests, and pilot release.
   Description: auditability, regression, release validation, deployment readiness.
   Dependencies: `E1-E5`.
   Story Points: `8`.

### User Stories
- `S1` As a user, I can sign in and access only my workspace so that sensitive legal information stays protected.
  Acceptance Criteria:
  - Given valid credentials, when I log in, then I receive a valid session.
  - Given invalid credentials, when I log in, then access is denied.
  - Given another user's case, when I try to access it without permission, then I receive `403`.
  Priority: `P0`
  Story Points: `5`
- `S2` As a firm admin, I can grant `read` or `read_write` access to a case so that my team can collaborate safely.
  Acceptance Criteria:
  - Given a firm admin, when access is granted, then the grant is stored.
  - Given a non-admin, when trying to share, then the request is denied.
  - Given a grant, when access is used, then the event is auditable.
  Priority: `P0`
  Story Points: `5`
- `S3` As a lawyer, I can create a case with required fields and initial state so that work starts from a valid expediente.
  Acceptance Criteria:
  - Given name and legal area, when I create the case, then it is stored.
  - Given missing required fields, when I create the case, then validation fails.
  - Given a created case, then status is `Pendiente de analisis`.
  Priority: `P0`
  Story Points: `3`
- `S4` As a lawyer, I can move a case through lifecycle states without losing history.
  Acceptance Criteria:
  - Given an allowed transition, when I update status, then it persists.
  - Given a closed or archived case, then history remains accessible.
  Priority: `P1`
  Story Points: `3`
- `S5` As a lawyer, I can upload supported documents and see processing status.
  Acceptance Criteria:
  - Given unsupported formats or oversize files, upload is rejected.
  - Given a valid file, then a document record and version are created.
  - Given processing starts, then status updates are visible.
  Priority: `P0`
  Story Points: `8`
- `S6` As a lawyer, scanned PDFs are OCR-processed and either made analyzable or marked insufficient.
  Acceptance Criteria:
  - Given a scanned PDF, when processing runs, then OCR is attempted.
  - Given low-quality extraction, then status becomes `Calidad insuficiente`.
  - Given insufficient quality, then analysis is blocked.
  Priority: `P0`
  Story Points: `5`
- `S7` As a lawyer, I can run a legal analysis that includes required sections and verified sources.
  Acceptance Criteria:
  - Given enough evidence, when analysis completes, then it includes all mandatory sections.
  - Given completed analysis, then at least `3` norms and `2` rulings are cited.
  - Given completed analysis, then corpus version and disclaimer are stored.
  Priority: `P0`
  Story Points: `8`
- `S8` As a lawyer, failed technical analyses refund consumed credit events.
  Acceptance Criteria:
  - Given a technical failure, then analysis status records the failure.
  - Given a consumed credit event, then a refund ledger entry is created.
  Priority: `P1`
  Story Points: `3`
- `S9` As a lawyer, I can ask legal questions and receive cited answers.
  Acceptance Criteria:
  - Given a valid question length, when I ask, then the response includes citations.
  - Given invalid length, then validation fails.
  - Given unverifiable citations, then the response is withheld.
  Priority: `P0`
  Story Points: `8`
- `S10` As a lawyer, I can attach a conversation to a case without auto-changing case data.
  Acceptance Criteria:
  - Given a linked conversation, then the link is stored.
  - Given chat activity, then no automatic mutation of case data occurs.
  Priority: `P1`
  Story Points: `3`
- `S11` As a lawyer, I can generate an editable `tutela` from case context and analysis.
  Acceptance Criteria:
  - Given prior analysis, when draft generation runs, then required sections are present.
  - Given a generated draft, then I can edit it.
  Priority: `P1`
  Story Points: `5`
- `S12` As a lawyer, I can generate an editable `derecho de peticion` with applicable regime.
  Acceptance Criteria:
  - Given draft generation, then required sections are present.
  - Given a recipient, then the applicable regime is identified.
  Priority: `P1`
  Story Points: `5`
- `S13` As a lawyer, I can export an analysis to PDF or DOCX.
  Acceptance Criteria:
  - Given an analysis, when export completes, then the file includes case name, date, results, sources, and disclaimer.
  Priority: `P1`
  Story Points: `3`
- `S14` As a team member, I can inspect complete case history.
  Acceptance Criteria:
  - Given a case, then analyses, chats, docs, generated docs, and share events appear chronologically.
  Priority: `P1`
  Story Points: `3`

### Tasks
- `T1` Backend auth + JWT + role model | Estimate: `10h` | Dependencies: none | DoD: login, register, refresh working with tests.
- `T2` Flutter auth shell + route guards | Estimate: `12h` | Dependencies: `T1` | DoD: protected navigation and session persistence.
- `T3` Case CRUD + lifecycle API | Estimate: `14h` | Dependencies: `T1` | DoD: endpoints, validation, and state tests complete.
- `T4` Case list/detail/history UI | Estimate: `18h` | Dependencies: `T2`, `T3` | DoD: users can create, view, and update cases with history.
- `T5` Upload pipeline + object storage + versioning | Estimate: `18h` | Dependencies: `T3` | DoD: supported files stored and versioned with metadata.
- `T6` Worker OCR/text extraction/status updates | Estimate: `20h` | Dependencies: `T5` | DoD: async processing works on sample docs.
- `T7` Chunking/embedding/pgvector indexing | Estimate: `16h` | Dependencies: `T6` | DoD: case chunks searchable with metadata.
- `T8` Legal corpus ingestion + source registry | Estimate: `16h` | Dependencies: none | DoD: norms and jurisprudence loaded and queryable.
- `T9` Retrieval orchestration + citation verifier | Estimate: `20h` | Dependencies: `T7`, `T8` | DoD: only verified citations pass.
- `T10` Analysis generation API + structured response | Estimate: `18h` | Dependencies: `T9` | DoD: required sections and min sources enforced.
- `T11` Chat API + conversation persistence | Estimate: `14h` | Dependencies: `T9` | DoD: cited answers stored and optionally linked to case.
- `T12` Draft generation + editor + export service | Estimate: `20h` | Dependencies: `T10` | DoD: editable drafts and PDF or DOCX export work.
- `T13` Sharing/ACL/audit events | Estimate: `14h` | Dependencies: `T1`, `T3` | DoD: firm admin can share and events are logged.
- `T14` End-to-end QA suite + fixtures | Estimate: `18h` | Dependencies: `T3-T13` | DoD: critical flows covered by regression tests.
- `T15` Deployment, monitoring, pilot hardening | Estimate: `16h` | Dependencies: `T10-T14` | DoD: staging and prod checklist passed.

## Sprint Planning

### Sprint 1
- Goal: deliver secure case management and document-to-knowledge pipeline.
- Capacity: `~150h`
- Included Epics: `E1`, `E2`, start `E3`, start `E6`
- Included Stories: `S1-S6`, `S14` partial
- Included Tasks: `T1-T8`, `T13` partial, `T14` partial
- Risks: corpus ingestion delays; OCR quality on poor scans.
- Success Criteria: user can create case, upload docs, see processing state, and obtain searchable case knowledge.

### Sprint 2
- Goal: deliver verified AI outputs, drafting, export, and pilot release.
- Capacity: `~150h`
- Included Epics: finish `E3`, `E4`, `E5`, `E6`
- Included Stories: `S7-S14`
- Included Tasks: `T9-T15`
- Risks: citation verifier false negatives; export formatting issues; performance tuning.
- Success Criteria: user can run grounded analysis, ask cited questions, generate editable drafts, export results, and pass QA sign-off.

## Team Allocation

- `Flutter Developer 1`: auth shell, case list/detail, history, share UI.
- `Flutter Developer 2`: document upload/status UI, analysis/chat screens, draft editor/export UI.
- `Backend Developer`: FastAPI monolith, auth, case APIs, ACL, history, export endpoints, DB schema.
- `AI Engineer`: OCR pipeline, chunking, embeddings, corpus ingestion, retrieval, verifier, analysis/chat orchestration.
- `QA Engineer`: acceptance criteria, test data, API/UI regression, security/access matrix, go-live validation.

## Risk Assessment

- Business risk: unresolved plans and credits (`RN-044` to `RN-048`) | Impact: `High` | Probability: `High` | Mitigation: feature-flag monetization, admin-configured limits.
- Business risk: legal corpus licensing and completeness | Impact: `High` | Probability: `Medium` | Mitigation: lock approved corpus sources before Sprint 1 ends.
- Technical risk: OCR quality on low-quality scans | Impact: `High` | Probability: `Medium` | Mitigation: quality scoring plus explicit `Calidad insuficiente` path.
- Technical risk: citation verification blocks too many responses | Impact: `High` | Probability: `Medium` | Mitigation: strict structured generation and corpus ID grounding.
- Security risk: cross-case data leakage | Impact: `Critical` | Probability: `Low-Med` | Mitigation: server-side case filters, ACL tests, prompt-context guards.
- Security risk: sensitive legal documents exposed via storage or logs | Impact: `Critical` | Probability: `Medium` | Mitigation: private buckets, signed URLs, log redaction, encryption.
- Scalability risk: large documents slow indexing and analysis | Impact: `Medium` | Probability: `Medium` | Mitigation: async jobs, chunk limits, background retries.
- Delivery risk: 2-week timeline too tight for full collaboration and billing | Impact: `High` | Probability: `High` | Mitigation: defer billing and advanced collaboration, keep monolith architecture.

## Final Recommendation

### Critical Path
`auth/RBAC -> case CRUD -> upload/versioning -> OCR/text extraction -> embeddings/indexing -> legal corpus ingestion -> retrieval/verifier -> analysis -> chat -> drafting/export -> QA hardening`

### Scope Reduction Suggestions
- Keep `Flutter Web` as the primary MVP client.
- Ship one analysis template only.
- Make `derecho de peticion` generation template-based if regime auto-detection slips.
- Keep sharing to explicit case grants only; no firm-wide folders.
- Keep plans and credits internal and admin-configured, not commercialized.

### Deployment Strategy
- Local: `Docker Compose`
- Staging and production: managed Postgres, Redis, object storage, API service, worker service.
- Release behind pilot feature flags: `sharing`, `credits`, `derecho_peticion` if needed.

### Go-Live Checklist
- Corpus loaded and versioned.
- ACL matrix tested for all roles.
- Citation verifier tested against real corpus entries.
- OCR tested on representative Colombian legal documents.
- Export files include disclaimer and sources.
- Audit trail visible for shared access.
- Backup and restore verified.
- Monitoring for failed jobs, slow analysis, and `424` blocked responses in place.
