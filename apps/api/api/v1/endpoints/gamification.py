from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from core.database import get_db
from models.user import User
from models.gamification import GamificationProfile, Badge, UserBadge
from api.v1.endpoints.auth import get_current_user

router = APIRouter()


@router.get("/profile")
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current user's gamification profile."""
    profile = db.query(GamificationProfile).filter(
        GamificationProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        # Create profile if it doesn't exist
        profile = GamificationProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    # Get user badges
    badges = db.query(Badge, UserBadge).join(
        UserBadge, Badge.id == UserBadge.badge_id
    ).filter(UserBadge.user_id == current_user.id).all()
    
    badge_list = []
    for badge, user_badge in badges:
        badge_list.append({
            "id": badge.id,
            "code": badge.code,
            "name": badge.name,
            "description": badge.description,
            "rarity": badge.rarity,
            "awarded_at": user_badge.awarded_at
        })
    
    return {
        "user_id": profile.user_id,
        "xp": profile.xp,
        "level": profile.level,
        "streak_days": profile.streak_days,
        "last_streak_at": profile.last_streak_at,
        "problems_solved": profile.problems_solved,
        "total_submissions": profile.total_submissions,
        "fastest_solve_sec": profile.fastest_solve_sec,
        "badges": badge_list
    }


@router.get("/leaderboard")
async def get_leaderboard(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get the leaderboard rankings."""
    profiles = db.query(GamificationProfile, User).join(
        User, GamificationProfile.user_id == User.id
    ).order_by(desc(GamificationProfile.xp)).limit(limit).all()
    
    leaderboard = []
    for rank, (profile, user) in enumerate(profiles, 1):
        leaderboard.append({
            "rank": rank,
            "user": {
                "id": user.id,
                "display_name": user.display_name
            },
            "xp": profile.xp,
            "level": profile.level,
            "streak_days": profile.streak_days,
            "problems_solved": profile.problems_solved
        })
    
    return {"leaderboard": leaderboard}


@router.get("/badges")
async def get_available_badges(db: Session = Depends(get_db)):
    """Get all available badges."""
    badges = db.query(Badge).all()
    
    return [
        {
            "id": badge.id,
            "code": badge.code,
            "name": badge.name,
            "description": badge.description,
            "rarity": badge.rarity,
            "criteria": badge.criteria_json
        }
        for badge in badges
    ]