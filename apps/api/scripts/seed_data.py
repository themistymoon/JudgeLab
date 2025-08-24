#!/usr/bin/env python3
"""Seed the database with initial data."""

import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session

from core.database import SessionLocal, engine
from core.security import get_password_hash
from models import Base
from models.gamification import Badge, GamificationProfile
from models.problem import Problem, ProblemDifficulty, ProblemStatus, TestCase
from models.settings import PlatformSettings
from models.user import User, UserRole


def create_users(db: Session):
    """Create initial users."""
    print("Creating users...")

    users = [
        {
            "email": "admin@judgelab.dev",
            "display_name": "Admin User",
            "role": UserRole.ADMIN,
            "password": "admin123"
        },
        {
            "email": "author@judgelab.dev",
            "display_name": "Problem Author",
            "role": UserRole.AUTHOR,
            "password": "author123"
        },
        {
            "email": "student@judgelab.dev",
            "display_name": "Test Student",
            "role": UserRole.STUDENT,
            "password": "student123"
        }
    ]

    for user_data in users:
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing:
            user = User(
                email=user_data["email"],
                display_name=user_data["display_name"],
                role=user_data["role"],
                hashed_password=get_password_hash(user_data["password"]),
                is_active=1
            )
            db.add(user)

            # Create gamification profile
            profile = GamificationProfile(user_id=user.id)
            db.add(profile)

    db.commit()
    print("Users created.")


def create_badges(db: Session):
    """Create initial badges."""
    print("Creating badges...")

    badges = [
        {
            "code": "first_ac",
            "name": "First Blood",
            "description": "First accepted solution",
            "criteria_json": {"type": "first_ac"},
            "rarity": "common"
        },
        {
            "code": "speed_demon",
            "name": "Speed Demon",
            "description": "Solve with 70% time remaining",
            "criteria_json": {"type": "speed_solve", "threshold": 0.7},
            "rarity": "rare"
        },
        {
            "code": "streak_7",
            "name": "Weekly Warrior",
            "description": "7-day solving streak",
            "criteria_json": {"type": "streak", "days": 7},
            "rarity": "epic"
        },
        {
            "code": "clutch_solve",
            "name": "Clutch Master",
            "description": "Solve with less than 30 seconds remaining",
            "criteria_json": {"type": "clutch", "threshold_sec": 30},
            "rarity": "legendary"
        }
    ]

    for badge_data in badges:
        existing = db.query(Badge).filter(Badge.code == badge_data["code"]).first()
        if not existing:
            badge = Badge(**badge_data)
            db.add(badge)

    db.commit()
    print("Badges created.")


def create_problems(db: Session):
    """Create sample problems."""
    print("Creating problems...")

    # Get author user
    author = db.query(User).filter(User.role == UserRole.AUTHOR).first()
    if not author:
        print("No author user found, skipping problem creation")
        return

    problems = [
        {
            "slug": "sum-array",
            "title": "Sum Array Elements",
            "statement_md": """# Sum Array Elements

Given an array of integers, return the sum of all elements.

## Input
- First line: integer N (1 ≤ N ≤ 1000), the number of elements
- Second line: N space-separated integers

## Output
- A single integer: the sum of all elements

## Example
```
Input:
5
1 2 3 4 5

Output:
15
```
""",
            "tags": ["array", "math", "easy"],
            "difficulty": ProblemDifficulty.EASY,
            "status": ProblemStatus.PUBLISHED,
            "testcases": [
                {"input": "5\n1 2 3 4 5", "output": "15", "is_sample": True},
                {"input": "1\n42", "output": "42", "is_sample": False},
                {"input": "3\n-1 0 1", "output": "0", "is_sample": False},
                {"input": "4\n100 200 300 400", "output": "1000", "is_sample": False}
            ]
        },
        {
            "slug": "two-sum",
            "title": "Two Sum",
            "statement_md": """# Two Sum

Given an array of integers and a target sum, return the indices of two numbers that add up to the target.

## Input
- First line: integer N (2 ≤ N ≤ 10000), the number of elements
- Second line: N space-separated integers
- Third line: integer TARGET, the target sum

## Output
- Two space-separated integers: the 0-based indices of the two numbers

## Example
```
Input:
4
2 7 11 15
9

Output:
0 1
```
""",
            "tags": ["array", "hash-table", "medium"],
            "difficulty": ProblemDifficulty.MEDIUM,
            "status": ProblemStatus.PUBLISHED,
            "testcases": [
                {"input": "4\n2 7 11 15\n9", "output": "0 1", "is_sample": True},
                {"input": "3\n3 2 4\n6", "output": "1 2", "is_sample": False},
                {"input": "2\n3 3\n6", "output": "0 1", "is_sample": False},
                {"input": "5\n1 5 3 7 9\n12", "output": "1 3", "is_sample": False}
            ]
        }
    ]

    for problem_data in problems:
        existing = db.query(Problem).filter(Problem.slug == problem_data["slug"]).first()
        if not existing:
            testcases_data = problem_data.pop("testcases")

            problem = Problem(
                **problem_data,
                created_by=author.id
            )
            db.add(problem)
            db.flush()  # Get the problem ID

            # Add testcases
            for i, tc_data in enumerate(testcases_data):
                testcase = TestCase(
                    problem_id=problem.id,
                    idx=i,
                    input_blob=tc_data["input"],
                    output_blob=tc_data["output"],
                    is_sample=1 if tc_data["is_sample"] else 0
                )
                db.add(testcase)

    db.commit()
    print("Problems created.")


def create_platform_settings(db: Session):
    """Create platform settings."""
    print("Creating platform settings...")

    defaults = PlatformSettings.get_defaults()

    for key, value in defaults.items():
        existing = db.query(PlatformSettings).filter(PlatformSettings.key == key).first()
        if not existing:
            setting = PlatformSettings(
                key=key,
                value=value,
                description=f"Default setting for {key}"
            )
            db.add(setting)

    db.commit()
    print("Platform settings created.")


def main():
    """Main seeding function."""
    print("Starting database seeding...")

    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        create_users(db)
        create_badges(db)
        create_problems(db)
        create_platform_settings(db)

        print("Database seeding completed successfully!")

    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
