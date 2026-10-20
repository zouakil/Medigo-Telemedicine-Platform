# Repository review

Review date: 20 October 2026.

## Assessment

MediGo has a useful end-to-end prototype structure: separate Django apps, migrations, patient and staff interfaces, real-time consultation handling, PDF prescriptions, and an independent hardware reader. It needed more than presentation work before publication. The main problems were committed runtime data, embedded relay credentials, missing dependencies, and incomplete authorization.

The current source is better prepared for a GitHub demonstration. This review is **not a certification that every behavior is correct or that the application is ready for real patient data**. The safe publication route for this existing checkout is a clean source export, with credential rotation and a review of redistribution rights.

## Scope

The original Git index contained 867 files. The review inventoried the tree, application modules, migrations, templates, source assets, reference JSON, deployment configuration, device reader, serialized model, generated files, and historical patch scripts. It removed 737 generated/backup files from tracking without deleting the local copies.

All inventoried Python source files were parsed and reference JSON was decoded. All 29 active HTML templates are compiled by the regression suite. Authentication, consultation API boundaries, WebSocket helpers, uploads, private files, device endpoints, dependency imports, and setup configuration received targeted review. Generated PDFs and medical images were classified as runtime/private data rather than used as public examples. Binary model contents and clinical statements were not independently validated.

Automated parsing and template compilation do not establish full line-by-line semantic review or 100% test coverage. Browser execution, timing behavior, production infrastructure, and physical hardware require separate tests.

## Changes made

| Area | Improvement |
| --- | --- |
| Repository hygiene | Ignore environment files, virtual environments, uploads, generated static files, databases, backups, and old patch scripts. Untrack existing generated files while preserving them locally. |
| Documentation | Add a French README with setup, architecture, requirements, PFA context, author credits, limitations, and publication instructions. Keep this technical report; omit separate contribution and security documents at the owner's request. |
| Dependencies | Move to the Django 5.2 family, add missing NumPy/joblib/scikit-learn/XGBoost dependencies, record resolved versions, and separate hardware requirements. Remove unused Gunicorn/django-fsm dependencies. |
| Configuration | Replace machine-specific trusted origins and embedded TURN credentials with environment configuration. Use Django's current `STORAGES` setting. |
| Docker | Add database/cache readiness checks, ignore runtime build artifacts, use Python 3.13 and `libgomp1`, and bind the development proxy to localhost. |
| Authentication | Make Django respect `est_actif`, preserve activation service compatibility, rotate the patient session key on login, and generate codes with `secrets`. |
| Consultation APIs | Require the assigned doctor for clinical writes, live AI/summary reads, sensor controls, and consultation-end notification. Restore CSRF checks on browser write endpoints. |
| WebSockets | Validate origins, require the patient's matching session, scope consultation lookup/message writes to the connected participant, and reject malformed message envelopes. |
| Chat | Render incoming text as text nodes; restrict image links to expected local paths. Require participant authorization before storing uploads, verify image contents, and limit size. |
| Media | Route private files through participant checks rather than an unrestricted Nginx alias. Restrict doctor prescription access to the assigned doctor. |
| Device API | Require a configured `X-Sensor-Key` token for sensor ingestion/discovery; update the reader to use it. |
| Importer | Accept an explicit CSV path, validate columns, avoid deleting the catalog on import, skip exact duplicates, and wrap CLI imports in a transaction. |
| AI | Make serialized XGBoost loading opt-in after a stalled load; preserve the existing rule-based fallback. |
| Verification | Add targeted regression tests, isolated test settings, and GitHub Actions. |

Django 4.2's support ended in April 2026; the selected 5.2 line is an LTS release. See [Django's installation FAQ](https://docs.djangoproject.com/en/5.2/faq/install/) and [release policy](https://www.djangoproject.com/download/).

## Validation and limits

- Dependencies installed in this checkout's `.venv`, using Python 3.13.15. System Python packages were not modified.
- `pip check`: passed.
- Django system checks: passed using isolated test settings.
- Migration drift check: no changes detected.
- Regression suite: **20 tests passed**.
- Manifest static collection: passed using temporary output, without replacing existing collected files.
- Regression tests cover allowed and denied consultation writes, malformed JSON, CSRF enforcement, account activation, private media, prescription ownership, uploads, device tokens, scoped WebSocket database access, template compilation, and rule-based fallback.
- Syntax validation: passed for 96 Python files, three JSON files, and two YAML files in the final source inventory.
- The original 72,757,392-byte model stalled while XGBoost deserialized its state. A diagnostic attempt was terminated after a 20-second timeout; an earlier attempt also failed to complete. Model loading/inference is therefore **unverified**, not reported as passing.
- Docker and Node.js were unavailable. Docker image builds, Compose startup, JavaScript execution, PostgreSQL/Redis integration, video calls across networks, and I2C measurements were not run.

Serialized model portability is not guaranteed across library versions; recover the original training environment and re-export/validate the artifact before enabling it. See [scikit-learn model persistence guidance](https://scikit-learn.org/stable/model_persistence.html). Package installation success does not prove model compatibility or clinical accuracy.

## Work still needed before a public deployment

1. **Publication history and credentials.** Older commits contain prescription/chat files and former TURN credentials. Rotate the relay credentials. Start a new repository from the clean export, or separately plan a history cleanup if preserving history is required. No history rewrite or remote push was performed.
2. **Patient authentication.** Six-digit reusable codes are still the patient login mechanism. Add rate limiting, attempt monitoring, expiration/recovery, and an appropriate stronger authentication flow. Prescription code verification also needs brute-force protection and should avoid codes in query strings.
3. **Complete authorization review.** Targeted endpoints were tightened, but historical patient summaries/dossier visibility, status endpoints, active sessions after patient deactivation, and every role/relationship combination need a consistent documented policy and broader integration coverage.
4. **State changes and races.** Some administrative actions still mutate state through GET links. Convert them to POST forms with CSRF checks. Consultation acceptance needs transactional locking and PostgreSQL concurrency tests; doctor presence needs multi-tab/disconnection handling.
5. **Input validation and error handling.** Several older views still return raw exception messages or swallow failures. Introduce validated request schemas, transaction boundaries, and consistent logging. Expand validation for numeric sensor input and clinical data. Upload database/storage failures need coordinated rollback.
6. **Browser security and maintainability.** Live chat rendering was fixed, but other dynamic HTML builders still need an escaping audit. Extract the large inline CSS/JavaScript blocks, test browser behavior, improve accessibility, and consider locally hosted fonts/icons plus a content security policy.
7. **Device routing and caching.** The reader chooses the latest active consultation globally. Introduce explicit device-to-consultation assignments before running multiple sessions. Sensor toggles use Django's default local-memory cache; use a shared cache for multiple application workers.
8. **Clinical and model evidence.** Supply training code, dependency versions, data provenance, evaluation results, calibration, and a model card. Review the manually coded prevalence multipliers and medicine suggestions. A generated PDF/stamp is not evidence of a qualified electronic signature.
   The consultation report service also contains an explicit TODO: its `red_flags` list is currently empty rather than populated from the consultation. Live detection and report inclusion should not be treated as equivalent.
9. **Deployment operations.** Provide TLS, correctly configured trusted proxy handling, short-lived TURN credentials, backups/restores, access logs with redaction, storage retention, and deployment-specific security checks. Compose remains a development configuration.
10. **Licensing and redistribution.** A local MIT license was added with copyright attributed only to Zakaria Ouakil, as explicitly requested. The README credits Zakaria Ouakil (project lead), Aya Adrif, and Imane Guihia for the PFA. Confirm separately that the model, reference datasets, branding, and medicine catalog may be redistributed.

## Suggested next milestones

- Run the full stack with synthetic data and complete a patient-to-doctor video consultation, image upload, measurement, and prescription download.
- Add real WebSocket handshake tests and PostgreSQL race tests alongside the current helper-level regressions.
- Recover the model training environment and produce a reproducible, evaluated model release.
- Split large consultation views/templates into smaller, testable components while preserving French/Arabic behavior.
