# Copilot Instructions for Osteo-Portal

## Project Overview
- **Architecture:** Two-tier full-stack app with a React frontend (`react-ui/`) and Flask API backend (`api-server-flask/`). Frontend and backend are decoupled and communicate via HTTP REST API.
- **Frontend:** React (JS), organized by feature in `src/views/`, `src/routes/`, and UI components in `src/ui-component/`.
- **Backend:** Flask (Python), main entrypoint is `api-server-flask/run.py`, routes in `api-server-flask/api/routes.py`, models in `api-server-flask/api/models.py`.
- **Uploads:** PDB files stored in `api-server-flask/uploads/pdb_files/` for molecule data.

## Developer Workflows
- **Start Backend (Flask):**
  - Docker: `cd api-server-flask && docker-compose up --build`
  - Manual: `cd api-server-flask && source env/bin/activate && pip install -r requirements.txt && flask run`
- **Start Frontend (React):**
  - `cd react-ui && npm install && npm start`
- **API Port:** Default is `5000`. Change with `flask run --port <PORT>`. Update frontend API URL in `react-ui/src/config/constant.js`.
- **Testing:** Backend tests in `api-server-flask/tests.py`. Frontend tests (if any) follow React conventions.

## Key Patterns & Conventions
- **API Endpoints:**
  - Auth: `/api/users/register`, `/api/users/login`, `/api/users/logout`
  - All API endpoints are prefixed with `/api/`.
- **Frontend-Backend Integration:**
  - Frontend expects backend at `http://localhost:5000/api/` (configurable).
  - Update API URL in `src/config/constant.js` for different environments.
- **Environment Management:**
  - Python virtualenv in `api-server-flask/env/`.
  - React environment variables in `react-ui/env.sample`.
- **Uploads:**
  - PDB files for molecules are uploaded to `api-server-flask/uploads/pdb_files/`.

## External Dependencies
- **React UI:** Uses standard React, with custom themes and layouts in `src/themes/`, `src/layout/`.
- **Flask API:** Uses Flask, Gunicorn (see `api-server-flask/Dockerfile`), and SQLite (`api-server-flask/api/db.sqlite3`).
- **Nginx:** Config in `api-server-flask/nginx/flask_api.conf` for production deployments.

## Example: Update API URL
```js
// react-ui/src/config/constant.js
const config = {
  ...
  API_SERVER: 'http://localhost:5000/api/' // Change this for different backend ports
};
```

## References
- See `README.md` for setup and workflow details.
- Key files: `api-server-flask/run.py`, `api-server-flask/api/routes.py`, `react-ui/src/config/constant.js`, `api-server-flask/tests.py`.

---
**For questions or unclear patterns, ask for clarification or check README.md.**
