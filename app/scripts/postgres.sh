docker run -d \
  --name backend-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=backend_db \
  -p 5432:5432 \
  -v pgdata:/var/lib/postgresql/data \
  postgres:16
