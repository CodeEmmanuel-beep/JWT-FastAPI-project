from app.core.celery_config import celery_app
from app.core.db import SessionLocal
from app.models_sql import Task
from sqlalchemy import select, or_
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
import requests

load_dotenv()
API_KEY = os.getenv("SENDGRID_API_KEY")
SENDER = os.getenv("SENDGRID_SENDER")


@celery_app.task(name="app.task.send_email")
def send_email_name(subject: str, body: str, to_email: str):
    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    data = {
        "personalizations": [{"to": [{"email": to_email}], "subject": subject}],
        "from": {"email": SENDER},
        "content": [{"type": "text/plain", "value": body}],
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"respomse: {response.status_code},  body: {response.text}")
    except Exception as e:
        print(f"failure: {e}")


@celery_app.task
def execute_task():
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        worker = (
            (
                db.execute(
                    select(Task).where(
                        Task.day_of_execution < now,
                        Task.complete.is_(False),
                        Task.status == "pending",
                    )
                )
            )
            .scalars()
            .all()
        )
        print(f"executing{len(worker)} tasks")
        for task in worker:
            task.status = "expired"
            send_email_name.delay(
                subject="expired deadline",
                body="sorry, your scheduled task has expired without accomplishment, wish you more strength next time",
                to_email=task.user.email,
            )
            print(f"updatedlen{task} tasks successfully")
        db.commit()
    except Exception as e:
        print(f"error encountered: {e}")
        db.rollback()
    finally:
        db.close()


@celery_app.task
def done_task():
    db = SessionLocal()
    now = datetime.now(timezone.utc)
    done = (
        db.execute(
            select(Task).where(
                Task.day_of_execution > now,
                Task.complete.is_(True),
                or_(Task.status == "pending", Task.status.is_(None)),
            )
        )
        .scalars()
        .all()
    )
    try:
        for task in done:
            task.status = "accomplished"
            send_email_name.delay(
                subject="Task accomplished!",
                body=f"congratulations are in other, your task, with Task ID {task.id}, and description {task.description}, have been accomplished before the deadline, this shows how commited you are, keep it up, cheers",
                to_email=task.user.email,
            )
        db.commit()
    except Exception as e:
        print(f"error: {e}")
        db.rollback()
    finally:
        db.close()
