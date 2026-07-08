import database
from database import SessionLocal
import models
import auth

models.Base.metadata.create_all(bind=database.engine)
db = SessionLocal()
user = db.query(models.EngineUser).filter(models.EngineUser.username == "admin").first()
if not user:
    new_user = models.EngineUser(username="admin", hashed_password=auth.get_password_hash("password123"))
    db.add(new_user)
    db.commit()
    print("Admin user created (username: admin, password: password123)")
else:
    print("Admin user already exists")
db.close()
