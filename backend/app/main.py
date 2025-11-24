# app/main.py
from datetime import date

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import json

from .database import Base, engine, get_db
from . import models
from .models import (
    User, WasteDeposit, EcoTreeHistory, VoucherRedemption,
    EducationContent, QuizQuestion, QuizAnswerHistory, MissionClaim
)
from .schemas import (
    Token, UserRegister, GoogleLoginPayload, UserProfileUpdate, UserOut,
    WasteScanResult, DepositCreate, DepositOut,
    DashboardSummary, CalendarResponse, CalendarDayActivity,
    GamificationStatus, MissionStatus, MissionClaimRequest,
    EducationOut, QuizQuestionOut, QuizAnswerIn, QuizAnswerResult,
    VoucherOption, RedeemRequest, VoucherOut, RewardBalance,
    LeaderboardUser, AdminSummary,
)
from .security import (
    hash_password, authenticate_user, create_access_token,
    get_current_user, require_admin,
)
from .gamification import (
    get_level_from_points, get_tree_stage, calculate_points,
    update_user_streak, ECO_TREE_XP_MAX, ECO_TREE_BONUS_POINTS,
    VOUCHER_OPTIONS, get_missions_for_user,
)

# Buat tabel di MySQL jika belum ada
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Ucollet API - Digital Innovation for a Sustainable Future",
    description="Backend FastAPI dengan MySQL untuk manajemen sampah, gamifikasi, dan voucher pulsa.",
    version="1.0.0",
)

# =========================================================
# 1. AUTH & USER
# =========================================================

@app.post("/auth/register", response_model=UserOut)
def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar")

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        domicile=payload.domicile,
        level="Bronze",
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Email atau password salah")
    token = create_access_token({"sub": user.id})
    return Token(access_token=token)


@app.post("/auth/google", response_model=Token)
def google_login(payload: GoogleLoginPayload, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.google_id == payload.google_id).first()
    if not user:
        existing = db.query(User).filter(User.email == payload.email).first()
        if existing and existing.google_id is None:
            existing.google_id = payload.google_id
            existing.photo_url = payload.photo_url or existing.photo_url
            existing.domicile = payload.domicile or existing.domicile
            db.add(existing)
            user = existing
        else:
            user = User(
                name=payload.name,
                email=payload.email,
                google_id=payload.google_id,
                photo_url=payload.photo_url,
                domicile=payload.domicile,
            )
            db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token({"sub": user.id})
    return Token(access_token=token)


@app.get("/users/me", response_model=UserOut)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@app.patch("/users/me", response_model=UserOut)
def update_my_profile(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.name is not None:
        current_user.name = payload.name
    if payload.domicile is not None:
        current_user.domicile = payload.domicile
    if payload.photo_url is not None:
        current_user.photo_url = payload.photo_url

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


# =========================================================
# 3. PENGELOLAAN SAMPAH (SCAN & MANUAL)
# =========================================================

@app.post("/waste/scan", response_model=WasteScanResult)
async def scan_waste(file: UploadFile = File(...)):
    filename = file.filename.lower()

    if any(x in filename for x in ["kaleng", "can", "alum"]):
        waste_name = "Kaleng minuman"
        category = "ANORGANIK_LOGAM"
        info = "Kaleng termasuk anorganik logam, sebaiknya dikumpulkan dan didaur ulang."
    elif any(x in filename for x in ["plastik", "botol"]):
        waste_name = "Botol plastik"
        category = "ANORGANIK_PLASTIK"
        info = "Plastik sulit terurai, jangan dibakar. Kumpulkan untuk bank sampah/daur ulang."
    elif any(x in filename for x in ["pisang", "organik"]):
        waste_name = "Sisa organik"
        category = "ORGANIK"
        info = "Sampah organik bisa dijadikan kompos, jangan dibuang sembarangan."
    else:
        waste_name = "Sampah campuran"
        category = "ORGANIK"
        info = "Pisahkan organik & anorganik, kurangi plastik sekali pakai."

    return WasteScanResult(waste_name=waste_name, category=category, info=info)


@app.post("/waste/deposits", response_model=DepositOut)
def create_deposit(
    payload: DepositCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category = payload.category.upper()
    if category not in ["ORGANIK", "ANORGANIK_PLASTIK", "ANORGANIK_LOGAM"]:
        raise HTTPException(status_code=400, detail="Kategori sampah tidak valid")

    points = calculate_points(category, payload.amount)

    deposit = WasteDeposit(
        user_id=current_user.id,
        date=date.today(),
        waste_name=payload.waste_name,
        category=category,
        amount=payload.amount,
        points_earned=points,
        via=payload.via,
    )
    db.add(deposit)

    # update user
    current_user.total_points += points
    current_user.level = get_level_from_points(current_user.total_points)
    current_user.total_waste_amount += payload.amount
    current_user.total_deposits += 1

    current_user.eco_xp += points
    if current_user.eco_xp >= ECO_TREE_XP_MAX:
        current_user.eco_xp = ECO_TREE_XP_MAX
        current_user.eco_tree_ready = True

    update_user_streak(current_user, date.today())

    db.add(current_user)
    db.commit()
    db.refresh(deposit)
    return deposit


@app.get("/waste/deposits", response_model=List[DepositOut])
def list_deposits(
    year: int | None = None,
    month: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(WasteDeposit).filter(WasteDeposit.user_id == current_user.id)

    if year and month:
        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1)
        else:
            end = date(year, month + 1, 1)
        q = q.filter(WasteDeposit.date >= start, WasteDeposit.date < end)

    q = q.order_by(WasteDeposit.date.desc(), WasteDeposit.id.desc())
    return q.all()
