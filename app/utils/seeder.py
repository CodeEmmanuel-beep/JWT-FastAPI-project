from app.core.db import SessionLocal
from app.models_sql import User, Share, Blog
from faker import Faker

fake = Faker()


def seed_data(num_users: int = 5, share: int = 3, blogs_per_user: int = 3):
    db = SessionLocal()
    try:
        for _ in range(num_users):
            user = User(
                username=fake.user_name(),
                email=fake.email(),
                age=66,
                name=fake.name(),
                nationality=fake.country(),
                password="hashed_password_placehoder",
            )
            db.add(user)
            db.flush()
            db.refresh(user)
            for _ in range(blogs_per_user):
                blog = Blog(
                    title=fake.sentence(),
                    content=fake.paragraph(),
                    user_id=user.id,
                    time_of_post=fake.date_time_this_month(),
                )
                db.add(blog)
                db.flush()
                db.refresh(blog)
                for _ in range(share):
                    shar = Share(
                        type="love",
                        content=fake.sentence(),
                        time_of_share=fake.date_time_this_year(),
                        blog_id=blog.id,
                        user_id=user.id,
                    )
                    db.add(shar)
                db.commit()
        print("completed faker")
    except Exception as e:
        db.rollback()
        print(f"failed during seeding: {e}")
    finally:
        db.close()
