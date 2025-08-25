import hashlib
import os
from datetime import UTC

from celery import Celery

from core.config import settings
from core.database import SessionLocal
from models.submission import Submission, SubmissionVerdict

# Initialize Celery
celery_app = Celery(
    "judgelab-judge",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def store_source_code(submission_id: int, source_code: str) -> str:
    """Store source code and return reference."""
    # Create artifacts directory if it doesn't exist
    artifacts_dir = "judge_artifacts"
    os.makedirs(artifacts_dir, exist_ok=True)

    # Generate hash-based filename
    code_hash = hashlib.sha256(source_code.encode()).hexdigest()[:16]
    filename = f"{submission_id}_{code_hash}.txt"
    filepath = os.path.join(artifacts_dir, filename)

    # Write source code to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(source_code)

    return filename


@celery_app.task
def submit_solution(submission_id: int, source_code: str):
    """Judge a submission (Celery task)."""
    db = next(get_db())

    try:
        # Get submission
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            return {"error": "Submission not found"}

        # Store source code
        source_ref = store_source_code(submission_id, source_code)
        submission.source_ref = source_ref
        submission.verdict = SubmissionVerdict.JUDGING
        db.commit()

        # TODO: Implement actual judging logic
        # For now, simulate judging with a simple result

        # Mock judging result
        verdict = SubmissionVerdict.AC  # Always accept for now
        time_ms = 100  # Mock execution time
        memory_kb = 1024  # Mock memory usage

        # Update submission with results
        submission.verdict = verdict
        submission.time_ms = time_ms
        submission.memory_kb = memory_kb

        from datetime import datetime
        submission.judged_at = datetime.now(UTC)

        db.commit()

        # TODO: Update gamification profile if AC

        return {
            "submission_id": submission_id,
            "verdict": verdict.value,
            "time_ms": time_ms,
            "memory_kb": memory_kb
        }

    except Exception as e:
        # Mark submission as system error
        submission.verdict = SubmissionVerdict.RE
        db.commit()
        raise e

    finally:
        db.close()
