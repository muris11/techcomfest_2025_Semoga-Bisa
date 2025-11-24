# app/schemas.py
from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel, EmailStr


# === Auth ===
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    domicile: Optional[str] = None


class GoogleLoginPayload(BaseModel):
    google_id: str
    email: EmailStr
    name: str
    photo_url: Optional[str] = None
    domicile: Optional[str] = None


# === User ===
class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    domicile: Optional[str] = None
    photo_url: Optional[str] = None


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    domicile: Optional[str]
    photo_url: Optional[str]
    total_points: int
    level: str
    total_waste_amount: float
    total_deposits: int
    trees_grown: int
    eco_xp: int
    eco_tree_ready: bool
    streak_current: int
    streak_longest: int

    class Config:
        from_attributes = True


# === Waste / Setoran ===
class WasteScanResult(BaseModel):
    waste_name: str
    category: str
    info: str


class DepositCreate(BaseModel):
    waste_name: str
    category: str
    amount: float = 1.0
    via: str = "manual"


class DepositOut(BaseModel):
    id: int
    date: date
    waste_name: str
    category: str
    amount: float
    points_earned: int
    via: str

    class Config:
        from_attributes = True


# === Dashboard & Kalender ===
class DashboardSummary(BaseModel):
    total_points: int
    level: str
    total_deposits: int
    total_waste_amount: float
    eco_tree_stage: str
    eco_tree_ready: bool
    trees_grown: int
    streak_current: int
    vouchers_active: int


class CalendarDayActivity(BaseModel):
    date: date
    total_deposits: int
    total_points: int


class CalendarResponse(BaseModel):
    year: int
    month: int
    days: List[CalendarDayActivity]
    streak_current: int
    streak_longest: int


# === Gamifikasi ===
class GamificationStatus(BaseModel):
    total_points: int
    level: str
    eco_xp: int
    eco_tree_stage: str
    eco_tree_ready: bool
    trees_grown: int
    streak_current: int
    streak_longest: int


class MissionStatus(BaseModel):
    code: str
    title: str
    description: str
    type: str   # DAILY / WEEKLY
    progress: int
    target: int
    status: str  # in_progress/available/claimed
    reward_points: int
    reward_eco_xp: int


class MissionClaimRequest(BaseModel):
    code: str


# === Edukasi & Kuis ===
class EducationOut(BaseModel):
    id: int
    title: str
    slug: str
    summary: Optional[str]
    body: str
    category: str

    class Config:
        orm_mode = True


class QuizQuestionOut(BaseModel):
    id: int
    question: str
    options: List[str]
    points_reward: int


class QuizAnswerIn(BaseModel):
    choice_index: int


class QuizAnswerResult(BaseModel):
    is_correct: bool
    points_awarded: int


# === Reward / Voucher ===
class VoucherOption(BaseModel):
    nominal: int
    cost: int


class RedeemRequest(BaseModel):
    nominal: int


class VoucherOut(BaseModel):
    id: int
    nominal: int
    points_spent: int
    status: str
    created_at: datetime

    class Config:
        orm_mode = True


class RewardBalance(BaseModel):
    total_points: int
    vouchers_active: int
    options: List[VoucherOption]


# === Komunitas & Admin ===
class LeaderboardUser(BaseModel):
    user_id: int
    name: str
    level: str
    total_points: int
    trees_grown: int


class AdminSummary(BaseModel):
    total_users: int
    total_deposits: int
    total_points_distributed: int
    total_vouchers_redeemed: int
