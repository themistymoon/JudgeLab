
from sqlalchemy.orm import Session

from models.problem import Problem, ProblemDifficulty, ProblemStatus
from schemas.problem import ProblemCreate, ProblemUpdate


def get_problems(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    difficulty: str | None = None,
    tags: list[str] | None = None
) -> list[Problem]:
    query = db.query(Problem).filter(Problem.status == ProblemStatus.PUBLISHED)

    if difficulty:
        query = query.filter(Problem.difficulty == ProblemDifficulty(difficulty))

    if tags:
        # Simple tag filtering - in production, consider using proper JSON queries
        for tag in tags:
            query = query.filter(Problem.tags.contains([tag]))

    return query.offset(skip).limit(limit).all()


def get_problem_by_slug(db: Session, slug: str) -> Problem | None:
    return db.query(Problem).filter(Problem.slug == slug).first()


def create_problem(db: Session, problem_data: ProblemCreate, creator_id: int) -> Problem:
    problem = Problem(
        **problem_data.model_dump(),
        created_by=creator_id
    )
    db.add(problem)
    db.commit()
    db.refresh(problem)
    return problem


def update_problem(db: Session, problem: Problem, problem_data: ProblemUpdate) -> Problem:
    update_data = problem_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(problem, field, value)

    problem.version += 1
    db.commit()
    db.refresh(problem)
    return problem
