PYTHON ?= python3
DOCKER ?= docker
DOCKER_IMAGE ?= g1-redis-project
DOCKER_SMOKE_PORT ?= 6379
DOCKER_NETWORK ?= g1-redis-project-smoke-net
DOCKER_SERVER_CONTAINER ?= g1-redis-project-smoke-server

.PHONY: run test-local smoke-local test-docker smoke-docker lint

run:
	$(PYTHON) -m src.main

test-local:
	$(PYTHON) -m pytest

smoke-local:
	$(PYTHON) scripts/smoke_test.py

test-docker:
	$(DOCKER) build -t $(DOCKER_IMAGE):test .
	$(DOCKER) run --rm $(DOCKER_IMAGE):test /bin/sh -lc "python -m pytest -q && python -m ruff check ."

smoke-docker:
	$(DOCKER) build -t $(DOCKER_IMAGE):smoke .
	$(PYTHON) scripts/docker_smoke.py --image $(DOCKER_IMAGE):smoke --network $(DOCKER_NETWORK) --container $(DOCKER_SERVER_CONTAINER) --port $(DOCKER_SMOKE_PORT)

lint:
	$(PYTHON) -m ruff check .
