from app.database.config import Base, engine
from app.models_sql import Task, Calculate, Market


print("Creating database tables....")
Base.metadata.create_all(bind=engine)
print("All tables created successfully")
