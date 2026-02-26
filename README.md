Hotel room booking (Django + Postgres).

## Run (Docker)

```bash
cp .env.example .env   # create .env from template (edit if needed)
docker compose up -d --build
```

Stop and remove containers:

```bash
docker compose down -v
```

Note: This removes volumes too. To keep the database volume, use `docker compose down`.

Open:
- http://localhost:8000/
- http://localhost:8000/admin/
- http://localhost:8000/api/docs/

Admin (auto-created):
- username: admin
- password: admin

Sample data:
- a few rooms are auto-seeded on startup

Auth (JWT):
- POST http://localhost:8000/api/auth/jwt/ (get access/refresh)
- POST http://localhost:8000/api/auth/jwt/refresh/ (refresh access)
- Use header: Authorization: Bearer <access>


Dev tools:
```bash
pip install -r requirements-dev.txt
ruff format .
ruff check .
mypy .
```
