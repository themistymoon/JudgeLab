
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.v1.endpoints.auth import get_current_user
from core.database import get_db
from models.problem import ProblemStatus, TestCase
from models.user import User, UserRole
from schemas.problem import (
    ProblemCreate,
    ProblemListResponse,
    ProblemResponse,
    ProblemUpdate,
    TestCaseCreate,
    TestCaseResponse,
)
from services.problem import create_problem, get_problem_by_slug, get_problems, update_problem

router = APIRouter()


@router.get("", response_model=list[ProblemListResponse])
async def list_problems(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    difficulty: str | None = None,
    tags: str | None = None,
    db: Session = Depends(get_db)
):
    """List published problems with optional filters."""
    tag_list = tags.split(",") if tags else None
    problems = get_problems(db, skip=skip, limit=limit, difficulty=difficulty, tags=tag_list)
    return [ProblemListResponse.model_validate(p) for p in problems]


@router.get("/{slug}", response_model=ProblemResponse)
async def get_problem(slug: str, db: Session = Depends(get_db)):
    """Get a problem by slug."""
    problem = get_problem_by_slug(db, slug)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    if problem.status != ProblemStatus.PUBLISHED:
        raise HTTPException(status_code=404, detail="Problem not found")

    return ProblemResponse.model_validate(problem)


@router.post("", response_model=ProblemResponse)
async def create_new_problem(
    problem_data: ProblemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new problem (author/admin only)."""
    if current_user.role not in [UserRole.AUTHOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # Check slug uniqueness
    existing = get_problem_by_slug(db, problem_data.slug)
    if existing:
        raise HTTPException(status_code=400, detail="Problem with this slug already exists")

    problem = create_problem(db, problem_data, current_user.id)
    return ProblemResponse.model_validate(problem)


@router.patch("/{slug}", response_model=ProblemResponse)
async def update_existing_problem(
    slug: str,
    problem_data: ProblemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a problem (author/admin only)."""
    if current_user.role not in [UserRole.AUTHOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    problem = get_problem_by_slug(db, slug)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    # Only allow author or admin to edit
    if problem.created_by != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Can only edit own problems")

    updated_problem = update_problem(db, problem, problem_data)
    return ProblemResponse.model_validate(updated_problem)


@router.get("/{slug}/testcases", response_model=list[TestCaseResponse])
async def get_problem_testcases(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get testcases for a problem (author/admin only, or samples for students)."""
    problem = get_problem_by_slug(db, slug)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    # Students can only see sample testcases
    if current_user.role == UserRole.STUDENT:
        testcases = db.query(TestCase).filter(
            TestCase.problem_id == problem.id,
            TestCase.is_sample == 1
        ).all()
    else:
        # Authors/admins can see all testcases
        if problem.created_by != current_user.id and current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Cannot access testcases")
        testcases = db.query(TestCase).filter(TestCase.problem_id == problem.id).all()

    return [TestCaseResponse.model_validate(tc) for tc in testcases]


@router.post("/{slug}/testcases", response_model=TestCaseResponse)
async def add_testcase(
    slug: str,
    testcase_data: TestCaseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a testcase to a problem (author/admin only)."""
    if current_user.role not in [UserRole.AUTHOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    problem = get_problem_by_slug(db, slug)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    if problem.created_by != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Can only edit own problems")

    testcase = TestCase(
        problem_id=problem.id,
        **testcase_data.model_dump()
    )
    db.add(testcase)
    db.commit()
    db.refresh(testcase)

    return TestCaseResponse.model_validate(testcase)
