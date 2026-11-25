.PHONY: test up down site install doctor
test:            ## run all tests
	cd packages/tracetune-py && PYTHONPATH=src python3 -m unittest discover -s tests -v
	cd services/ingest && go vet ./...
	cd crates/tracecore && cargo check
up:              ## start the local stack
	docker compose up --build
down:
	docker compose down
site:            ## run the website locally
	cd apps/web && npm install && npm run dev
install:         ## set up Python venv and build Go/Rust (Linux)
	bash scripts/install.sh
doctor:          ## check which tools are installed
	bash scripts/doctor.sh
