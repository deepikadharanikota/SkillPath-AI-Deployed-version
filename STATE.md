# Project State & Updates

This document tracks the structural changes, updates, and bug fixes applied to **Skillpath-AI** during its migration from a monolithic Streamlit application to a robust 3-Tier Microservice Architecture.

## 1. Architectural Overhaul (3-Tier Migration)
- **Frontend (Streamlit)**: Extracted purely UI components into a thin client (`frontend/main.py`). The frontend now communicates exclusively via API calls to the backend rather than executing local ML/logic functions.
- **Backend (FastAPI)**: Created a dedicated REST API service (`backend/main.py`) that handles all core business logic, Reinforcement Learning (DQN), database transactions, and data parsing.
- **Directories**: Restructured the root repository by moving relevant files into `frontend/` and `backend/` directories.

## 2. Dockerization & Orchestration
- **Service Dockerfiles**: Created individual `Dockerfile` configurations for both the `frontend` and `backend`.
- **Docker Compose**: Implemented `docker-compose.yml` to orchestrate 4 interconnected services:
  - `frontend`: Vite React app running on port `8503`.
  - `backend`: FastAPI app running on port `8002`.
  - `db`: PostgreSQL 18 container (mapped on host port `5434`).
  - `redis`: Redis container for caching and session management (mapped on host port `6381`).

## 3. Database & Persistence Layer
- **PostgreSQL 18 Integration**: Replaced local file/state caching with a persistent Postgres database using `asyncpg` and SQLAlchemy.
- **Data Models**: Created SQLAlchemy models in `backend/models.py`:
  - `User`: Stores GitHub SSO details.
  - `UserState`: Stores current learning progress, fatigue, and target roles.
  - `QuizHistory`: Logs scores and rewards for DQN training.
- **SQLAlchemy Fixes**: Configured `expire_on_commit=False` on the async `sessionmaker` to resolve `MissingGreenlet` lazy-loading crashes during async database transactions.

## 4. Authentication (GitHub SSO)
- **Redis Sessions**: Implemented Redis (`backend/redis_client.py`) to manage unique session tokens, ensuring complete session isolation between different users.
- **Server-Side OAuth State in Redis**: Replaced cookie-based session state with Redis-backed state validation (`oauth_state:<state>` with a 10-minute expiration) to avoid browser cross-site cookie drops on HTTPS-to-HTTP redirects.
- **Direct Async Token Exchange**: Migrated GitHub token and profile retrieval to direct async calls via `httpx.AsyncClient` in `backend/routers/auth.py`.
- **Environment Variables**: Consolidated credentials into a `.env` file (`GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`) managed by Docker Compose.

## 5. Bug Fixes & Refinements
- **Quiz Determinism Bug**: Resolved the issue in `backend/routers/quiz.py` where quiz options were appearing in the exact same order every time. The options (`opts`) are now dynamically shuffled using `random.shuffle()` per API request, and the correct answer index (`ans`) is automatically recalibrated.
- **Frontend Redirects**: Separated the internal Docker network URL (`backend:8002`) from the public-facing URL (`localhost:8002`) in the frontend to ensure the browser accurately follows the GitHub login redirect.

## 6. Dynamic Real-Time Fetching
- **YouTube Integration**: Removed the static, hardcoded `VIDEO_DB`. Added the `youtube-search-python` dependency to scrape and serve video recommendations dynamically based on the current `topic`, `difficulty`, and `module`. 
- **Roles API**: Removed the hardcoded frontend dropdown for target roles. Introduced a new `/roles` API endpoint in `backend/main.py` so the frontend fetches and populates the available roles dynamically based on backend configurations.

## 7. Topic Routing & DQN Retraining
- **Role to Topic Mapping**: Resolved a bug where selecting "DevOps Engineer" incorrectly defaulted to a "Python" learning journey due to unordered skill-gap mapping. Implemented a strict `ROLE_TO_TOPIC` dictionary in `backend/data.py` to ensure role selections deterministically map to their intended foundational topic.
- **DQN State Dimensions**: Safely expanded the environment's state vector (from 12 to 13 dimensions) to support the newly added "DevOps" topic. Executed an offline retraining of the neural network (`train_offline.py`) to generate new weight matrices (`dqn_weights.pkl`) compatible with the upgraded state architecture.

## 8. OAuth CSRF State Mismatch & Container Synchronization Fix

### Code-Level Changes
- **`backend/routers/auth.py`**:
  - **Eliminated Cookie Dependency for CSRF State**: Replaced Authlib's default Starlette `request.session` cookie mechanism with server-side Redis storage (`oauth_state:<state>` with a 600s TTL). This completely resolved the `{"detail":"mismatching_state: CSRF Warning! State not equal in request and response."}` error caused by modern browsers omitting `SameSite=Lax` cookies on redirects from HTTPS (`https://github.com`) to local HTTP (`http://localhost:8000`).
  - **Direct OAuth2 Flow via `httpx`**: Implemented direct async exchange with `https://github.com/login/oauth/access_token` and `https://api.github.com/user` using `httpx.AsyncClient`.
  - **Private GitHub Email Fallback**: Added automated lookup to `https://api.github.com/user/emails` to fetch verified primary emails for GitHub users who keep their public profile emails hidden.
  - **Graceful Error Handling & Redirects**: Replaced raw `HTTPException(400)` with client redirects to `FRONTEND_URL/?error=<encoded_message>`, ensuring the user is never stranded on a raw JSON error page on the backend (`localhost:8000/auth/callback`).
- **`frontend/main.py`**:
  - **UI Error Feedback**: Added query parameter check `if "error" in st.query_params:` in `render_login()` to render visible error notifications (`st.error`) in the Streamlit UI whenever an authentication failure or cancellation occurs.

### Docker Compose-Level Changes
- **`docker-compose.yml`**:
  - **Frontend URL Routing**: Added `FRONTEND_URL=http://localhost:8503` to the backend container's environment variables to configure explicit redirects back to Streamlit/frontend.
  - **Live-Reload Volume Mounts**: Configured volume mounts for both application tiers (`./backend:/app` and `./frontend:/app`), ensuring local code changes take effect immediately without requiring full container rebuilds.

