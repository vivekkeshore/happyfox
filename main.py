import logging.config

import uvicorn
from fastapi import FastAPI

from app.apis import API_ROUTERS

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s | %(module)s | %(lineno)d | %(levelname)s | %(message)s")

doc_summary = "APIs to manage the gmail operations, rules and actions."

app = FastAPI(
	title="Email Manager APIs",
	summary=doc_summary,
	version="0.0.1",
	contact={
		"name": "Vivek Keshore",
		"email": "vivek.keshore@gmail.com",
	},
)

# Registering all routes
for router, kwargs in API_ROUTERS:
	app.include_router(router, **kwargs)


if __name__ == "__main__":
	uvicorn.run("main:app", port=5010, reload=True)
