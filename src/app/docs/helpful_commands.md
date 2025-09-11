### Some commands for quick reference

view datatables
docker compose exec postgres \
  psql -U risk -d risk -c '\d+ training_samples'

docker compose exec postgres \
  psql -U risk -d risk -c '\d+ predictions'

start uvicorn reload sesh
uvicorn app.main:app --reload

docker compose down
docker compose up -d




# update db
alembic revision --autogenerate -m "resize embedding vector to 3456"
alembic upgrade head


docker compose exec postgres env | grep POSTGRES_
That will list POSTGRES_USER, POSTGRES_PASSWORD, and POSTGRES_DB, which together form the URL.

docker compose down -v
docker compose build api
docker compose up -d