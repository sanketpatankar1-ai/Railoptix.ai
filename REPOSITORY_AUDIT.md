# RailOptix Repository Audit

## 1. Current Architecture
- **Frontend**: React 19, Vite 8, TailwindCSS
- **Backend**: FastAPI, Python 3.14, SQLAlchemy, Pydantic
- **Database**: PostgreSQL (Local/Supabase compatibility)
- **AI/ML**: Google OR-Tools CP-SAT (Block Scheduling Optimizer), XGBoost (Scoring, stubbed/simulated), Google Gemini 2.5 (LLM Assistant with RAG)
- **Deployment Strategy**: Vercel/Render compatibility with Procfile and render.yaml

## 2. Implemented Features
- JWT-based authentication and role-based access control (RBAC).
- Maintenance task creation, ingestion, and persistence.
- Multi-department scheduling synchronization (Engineering, Signal & Telecom, Traction Distribution).
- Google OR-Tools CP-SAT based Gantt schedule generation and multi-department shadow bundling.
- Schedule approval and rejection workflow.
- Zonal and corridor mapping support (18 zones, 58 corridors).
- LLM AI Assistant (Gemini) capable of querying tasks and schedules contextually.

## 3. Partially Implemented Features
- Real-time Train Timetable Conflict Checking: The schema exists but depends on static/mock seed data rather than live NTES API integrations.
- XGBoost/SHAP: Features exist for scoring but rely on simulated weights and stubbed models if real trained artifacts aren't present.

## 4. Demo/Mock Features
- `seed_data.py`: Provides 13 demo users, 58 corridors, and a large dataset of generated tasks for testing the CP-SAT engine.
- Traffic data and historical maintenance data relies on synthetic distributions.

## 5. Known Bugs
- Frontend previously generated full ISO datetime strings causing FastAPI 422 Unprocessable Entity errors on `POST /api/tasks`. (Partially addressed via `.split('T')[0]`, but the underlying frontend contract should be double-checked).
- UI state reset bugs during schedule generation (fixed `setFilterCorridor` crash in previous session).

## 6. Technical Debt
- Lack of robust E2E testing framework (Playwright/Cypress).
- Heavy monolithic UI components could be split into smaller, reusable bits.
- Hardcoded timeout boundaries in Vite proxy (60s).

## 7. Documentation Problems
- Missing detailed internal architecture docs (API, DB, AI, Optimization).
- README is comprehensive but lacks structural separation and professional GitHub open-source polish.
- Missing PR/Issue templates and GitHub CI/CD workflows.

## 8. Security Issues
- `.env.example` previously contained realistic placeholders (fixed).
- Seed passwords are included but clearly marked for demo purposes.
- Safe CORS policies implemented.

## 9. GitHub Presentation Problems
- Missing `.github/` structure.
- Missing screenshots folder and embedded imagery in README.
- Lacking granular topic tags and a crisp GitHub project description.

## 10. Recommended Improvements
- Restructure documentation into a `docs/` folder.
- Implement comprehensive Mermaid diagrams in README.
- Add GitHub Actions CI workflow to validate PRs and test Python backend.
- Enhance UI/UX for a "government-tier" professional dashboard feel.
