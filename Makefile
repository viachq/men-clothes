.PHONY: run backend admin client

run:
	uv run uvicorn backend.main:app --reload

admin:
	cd admin && npm run dev

client:
	cd client && npm run dev
