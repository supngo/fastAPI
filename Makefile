.PHONY: run init seed format

run:
	uvicorn app.main:app --reload

init:
	python -m app.scripts.init_db

seed:
	python -m app.scripts.seed_db

format:
	black app
