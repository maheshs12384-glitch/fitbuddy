import json
import os
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fitbuddy.db")
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(40), unique=True, index=True, nullable=False)
    username = Column(String(60), nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    goal = Column(String(60), nullable=False)
    intensity = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    plan = relationship("Plan", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Plan(Base):
    __tablename__ = "plans"
    id = Column(Integer, primary_key=True)
    user_pk = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    original_plan = Column(Text, nullable=False)   # JSON
    updated_plan = Column(Text, nullable=True)     # JSON (after feedback)
    nutrition_tip = Column(Text, default="")
    last_feedback = Column(Text, default="")
    user = relationship("User", back_populates="plan")


def init_db():
    Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_user(db, data) -> User:
    """Create the user, or refresh their details if the user_id already exists."""
    user = get_user(db, data.user_id)
    if user is None:
        user = User(user_id=data.user_id)
        db.add(user)
    user.username, user.age, user.weight = data.username, data.age, data.weight
    user.goal, user.intensity = data.goal, data.intensity
    db.commit()
    db.refresh(user)
    return user


def save_plan(db, user: User, plan: dict, tip: str) -> Plan:
    row = user.plan or Plan(user_pk=user.id)
    row.original_plan, row.updated_plan = json.dumps(plan), None
    row.nutrition_tip, row.last_feedback = tip, ""
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_plan(db, user: User, plan: dict, feedback: str) -> Plan:
    user.plan.updated_plan = json.dumps(plan)
    user.plan.last_feedback = feedback
    db.commit()
    return user.plan


def get_user(db, user_id: str):
    return db.query(User).filter(User.user_id == user_id).first()


def get_original_plan(db, user_id: str):
    user = get_user(db, user_id)
    return json.loads(user.plan.original_plan) if user and user.plan else None


def get_all_users(db):
    return db.query(User).order_by(User.created_at.desc()).all()


def get_all_plans(db):
    return db.query(Plan).all()


def delete_user(db, user_id: str) -> bool:
    user = get_user(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True
