from fastapi import APIRouter

from api.v1.endpoints import attempts, auth, gamification, integrity, problems, submissions

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(problems.router, prefix="/problems", tags=["Problems"])
api_router.include_router(attempts.router, prefix="/attempts", tags=["Attempts"])
api_router.include_router(submissions.router, prefix="/submissions", tags=["Submissions"])
api_router.include_router(integrity.router, prefix="/integrity", tags=["Integrity"])
api_router.include_router(gamification.router, prefix="/gamification", tags=["Gamification"])
