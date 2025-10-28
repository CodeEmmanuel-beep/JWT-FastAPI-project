from app.routes import tasks_sql, calculations_sql, market_sql
from app.routes import task_auth, market_auth, Calculation_auth
from fastapi import FastAPI
import uvicorn
import os

app = FastAPI(title="Three Dimensions", version="1.0")

app.include_router(Calculation_auth.router)
app.include_router(market_auth.router)
app.include_router(task_auth.router)
app.include_router(tasks_sql.router)
app.include_router(calculations_sql.router)
app.include_router(market_sql.router)


@app.get("/", include_in_schema=False)
def home_page():
    return {
        "message": "Welcome to Three Dimensions API. Visit /docs to explore the endpoints."
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
