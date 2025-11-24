# app/models.py
from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Date,
    Float, ForeignKey, Text
)
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    google_id = Column(String(255), unique=True, nullable=True)

    domicile = Column(String(255), nullable=True)
    photo_url = Column(String(255), nullable=True)

    total_points = Column(Integer, default=0)
    level = Column(String(50), default="Bronze")

    total_waste_amount = Column(Float, default=0.0)
    total_deposits = Column(Integer, default=0)

    trees_grown = Column(Integer, default=0)
    eco_xp = Column(Integer, default=0)
    eco_tree_ready = Column(Boolean, default=False)
    streak_current = Column(Integer, default=0)
    streak_longest = Column(Integer, default=0)
    last_deposit_date = Column(Date, nullable=True)

    role = Column(String(20), default="user")  # user / admin

    created_at = Column(DateTime, default=datetime.utcnow)

    deposits = relationship("WasteDeposit", back_populates="user")
    vouchers = relationship("VoucherRedemption", back_populates="user")
    mission_claims = relationship("MissionClaim", back_populates="user")


class WasteDeposit(Base):
    __tablename__ = "waste_deposits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, default=date.today)
    waste_name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    amount = Column(Float, default=1.0)
    points_earned = Column(Integer, default=0)
    via = Column(String(20), default="manual")

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="deposits")


class EcoTreeHistory(Base):
    __tablename__ = "eco_tree_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tree_number = Column(Integer, nullable=False)
    bonus_points = Column(Integer, default=0)
    completed_at = Column(DateTime, default=datetime.utcnow)


class VoucherRedemption(Base):
    __tablename__ = "voucher_redemptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    nominal = Column(Integer, nullable=False)
    points_spent = Column(Integer, nullable=False)
    status = Column(String(20), default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="vouchers")


class EducationContent(Base):
    __tablename__ = "education_contents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False)
    summary = Column(Text, nullable=True)
    body = Column(Text, nullable=False)
    category = Column(String(50), default="general")
    created_at = Column(DateTime, default=datetime.utcnow)


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("education_contents.id"), nullable=True)
    question = Column(Text, nullable=False)
    options_text = Column(Text, nullable=False)  # JSON string: ["A", "B", ...]
    correct_index = Column(Integer, nullable=False)
    points_reward = Column(Integer, default=10)

    content = relationship("EducationContent")


class QuizAnswerHistory(Base):
    __tablename__ = "quiz_answers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("quiz_questions.id"), nullable=False)
    is_correct = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class MissionClaim(Base):
    __tablename__ = "mission_claims"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mission_code = Column(String(50), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    claimed_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="mission_claims")
