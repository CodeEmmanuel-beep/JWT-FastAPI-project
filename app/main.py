from app.routes import tasks_sql, calculations_sql, market_sql
from app.routes import task_auth, market_auth, Calculation_auth
from fastapi import FastAPI


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
        "message": "You have come a long way, finally deployed, Visit /docs to explore the endpoints."
    }
