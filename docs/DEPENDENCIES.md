# Third-party dependency inventory

Dependencies are pinned in `frontend/package-lock.json` and `backend/requirements.lock`; the backend lock includes transitive packages observed in the container. Full package/version/license metadata is committed in `frontend-dependencies.json` and `backend-dependencies.json`. These are inventories, not legal advice. Upstream LICENSE texts remain in installed packages/images.

| Component | Version | License / purpose |
| --- | --- | --- |
| React / React DOM | 19.1.1 | MIT; interface |
| React Router DOM | 7.18.4 | MIT; navigation |
| Plotly.js dist | 3.1.0 | MIT; local charts |
| React Flow | 12.8.4 | MIT; observed graph |
| Dagre | 1.1.5 | MIT; graph layout |
| Inter font | 5.2.6 package | SIL Open Font License 1.1; bundled fonts |
| Vite | 7.3.7 | MIT; build tooling |
| TypeScript | 5.9.2 | Apache-2.0; type checking |
| Playwright | 1.55.1 | Apache-2.0; transient Chromium tests |
| Swagger UI dist | 5.30.2 | Apache-2.0; locally bundled API documentation |
| FastAPI | 0.116.1 | MIT; API |
| SQLAlchemy | 2.0.43 | MIT; database layer |
| Alembic | 1.16.5 | MIT; migrations |
| psycopg / binary | 3.2.10 | LGPL-3.0; PostgreSQL driver |
| Argon2 CFFI | 25.1.0 | MIT; password hashing |
| Pydantic | 2.11.7 | MIT; validation |
| Uvicorn | 0.35.0 | BSD-3-Clause; HTTP server |
| pytest | 8.4.2 | MIT; tests |
| PostgreSQL image | 17.6-bookworm | PostgreSQL license plus Debian package licenses |
| nginx image | 1.28.0-alpine | BSD-2-Clause plus Alpine package licenses |
| Python build/runtime | 3.13.7-slim-bookworm | PSF license plus Debian packages |
| Node build tool | 22.19.0-bookworm-slim | Node MIT and bundled dependency licenses |

Frontend npm audit reported zero known vulnerabilities after patched router/Vite/Playwright versions were locked. This is the npm advisory result at verification time, not a guarantee that every base image or package is free from vulnerabilities. The newer Playwright 1.64 image was unavailable at the registry, so the verified compatible test package/image is 1.55.1.

To regenerate inventories with containers, execute `python -m app.inventory` in the backend and `node frontend/scripts/inventory.cjs` with the frontend working directory in a Node container. Source and generated inventory contain no secrets.
