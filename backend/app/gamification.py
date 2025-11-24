# app/gamification.py
from datetime import date, timedelta
from typing import List, Dict

from sqlalchemy.orm import Session

from .models import WasteDeposit, MissionClaim, User

# Level
LEVELS = [
    ("Bronze", 0),
    ("Silver", 1000),
    ("Gold", 5000),
    ("Platinum", 15000),
    ("Diamond", 30000),
]

# Pohon hijau
ECO_TREE_XP_MAX = 1000
ECO_TREE_BONUS_POINTS = 200

# Voucher pulsa
VOUCHER_OPTIONS = [
    {"nominal": 10000, "cost": 1000},
    {"nominal": 20000, "cost": 1800},
    {"nominal": 50000, "cost": 4000},
]


def get_level_from_points(points: int) -> str:
    level_name = "Bronze"
    for name, threshold in LEVELS:
        if points >= threshold:
            level_name = name
    return level_name


def get_tree_stage(eco_xp: int) -> str:
    if eco_xp <= 0:
        return "Bibit"
    ratio = eco_xp / ECO_TREE_XP_MAX
    if ratio < 0.25:
        return "Tunas"
    elif ratio < 0.5:
        return "Pohon kecil"
    elif ratio < 1.0:
        return "Pohon sedang"
    else:
        return "Pohon lebat"


def calculate_points(category: str, amount: float) -> int:
    base_per_unit = {
        "ORGANIK": 5,
        "ANORGANIK_PLASTIK": 10,
        "ANORGANIK_LOGAM": 15,
    }
    base = base_per_unit.get(category.upper(), 5)
    return int(base * max(amount, 0.0))


def update_user_streak(user: User, deposit_date: date):
    if user.last_deposit_date is None:
        user.streak_current = 1
    else:
        if deposit_date == user.last_deposit_date:
            pass
        elif deposit_date == user.last_deposit_date + timedelta(days=1):
            user.streak_current += 1
        else:
            user.streak_current = 1
    user.last_deposit_date = deposit_date
    if user.streak_current > user.streak_longest:
        user.streak_longest = user.streak_current


def get_week_range(d: date):
    start = d - timedelta(days=d.weekday())
    end = start + timedelta(days=6)
    return start, end


# === Mission helper (dipakai di endpoint) ===
from .schemas import MissionStatus  # hindari circular import, aman kalau dipakai hanya di runtime
from datetime import date as _date


def get_missions_for_user(db: Session, user: User) -> List[MissionStatus]:
    today = _date.today()
    week_start, week_end = get_week_range(today)

    missions: List[MissionStatus] = []

    # Misi 1: Setor sampah 3 hari berturut-turut
    code = "DAILY_STREAK_3"
    target = 3
    progress = min(user.streak_current, target)
    reward_points = 50
    reward_eco_xp = 50

    claim_exists = (
        db.query(MissionClaim)
        .filter(
            MissionClaim.user_id == user.id,
            MissionClaim.mission_code == code,
            MissionClaim.period_start == today,
            MissionClaim.period_end == today,
        )
        .first()
    )

    if claim_exists:
        status_m = "claimed"
    else:
        if user.streak_current >= target:
            status_m = "available"
        else:
            status_m = "in_progress"

    missions.append(
        MissionStatus(
            code=code,
            title="Setor sampah 3 hari berturut-turut",
            description="Pertahankan streak 3 hari.",
            type="DAILY",
            progress=progress,
            target=target,
            status=status_m,
            reward_points=reward_points,
            reward_eco_xp=reward_eco_xp,
        )
    )

    # Misi 2: Kumpulkan 5 kaleng (logam) dalam seminggu
    code2 = "WEEKLY_CAN_5"
    target2 = 5
    cans_count = (
        db.query(WasteDeposit)
        .filter(
            WasteDeposit.user_id == user.id,
            WasteDeposit.category == "ANORGANIK_LOGAM",
            WasteDeposit.date >= week_start,
            WasteDeposit.date <= week_end,
        )
        .count()
    )
    progress2 = min(cans_count, target2)
    reward_points2 = 100
    reward_eco_xp2 = 100

    claim_exists2 = (
        db.query(MissionClaim)
        .filter(
            MissionClaim.user_id == user.id,
            MissionClaim.mission_code == code2,
            MissionClaim.period_start == week_start,
            MissionClaim.period_end == week_end,
        )
        .first()
    )

    if claim_exists2:
        status2 = "claimed"
    else:
        if cans_count >= target2:
            status2 = "available"
        else:
            status2 = "in_progress"

    missions.append(
        MissionStatus(
            code=code2,
            title="Kumpulkan 5 kaleng dalam seminggu",
            description="Setorkan minimal 5 kaleng (logam) dalam 1 minggu.",
            type="WEEKLY",
            progress=progress2,
            target=target2,
            status=status2,
            reward_points=reward_points2,
            reward_eco_xp=reward_eco_xp2,
        )
    )

    return missions
