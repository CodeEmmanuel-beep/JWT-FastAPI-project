from body.database.config import Base, engine
from body.models_sql import Task, Market, Calculate

print("Creating database tables....")
Base.metadata.create_all(bind=engine)
print("All tables created successfully")
