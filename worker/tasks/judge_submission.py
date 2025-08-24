import os
from datetime import datetime
from typing import Dict, Any

import structlog
from celery import current_task

from database import get_db
from models import Submission, Problem, TestCase, SubmissionVerdict
from judge.executor import DockerExecutor
from judge.checker import Checker, CheckerResult
from config import settings

logger = structlog.get_logger()


def judge_submission(submission_id: int, source_code: str) -> Dict[str, Any]:
    """
    Judge a submission against test cases.
    This is the main Celery task for judging.
    """
    db = next(get_db())
    
    try:
        # Get submission and problem
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            logger.error("Submission not found", submission_id=submission_id)
            return {"error": "Submission not found"}
        
        problem = db.query(Problem).filter(Problem.id == submission.problem_id).first()
        if not problem:
            logger.error("Problem not found", problem_id=submission.problem_id)
            return {"error": "Problem not found"}
        
        # Get test cases
        testcases = db.query(TestCase).filter(
            TestCase.problem_id == problem.id
        ).order_by(TestCase.group, TestCase.idx).all()
        
        if not testcases:
            logger.error("No test cases found", problem_id=problem.id)
            return {"error": "No test cases found"}
        
        # Store source code
        source_ref = _store_source_code(submission_id, source_code)
        submission.source_ref = source_ref
        submission.verdict = SubmissionVerdict.JUDGING
        db.commit()
        
        logger.info(
            "Starting to judge submission",
            submission_id=submission_id,
            problem_id=problem.id,
            language=submission.lang.value,
            testcases_count=len(testcases)
        )
        
        # Initialize executor
        executor = DockerExecutor()
        
        # Judge each test case
        results = []
        total_time = 0
        max_memory = 0
        first_failed_test = None
        overall_verdict = SubmissionVerdict.AC
        
        for i, testcase in enumerate(testcases):
            logger.info(f"Running test case {i+1}/{len(testcases)}")
            
            # Update task progress
            if current_task:
                current_task.update_state(
                    state='PROGRESS',
                    meta={'current': i+1, 'total': len(testcases)}
                )
            
            # Execute code
            exec_result = executor.execute(
                language=submission.lang.value,
                source_code=source_code,
                input_data=testcase.input_blob,
                time_limit_ms=problem.time_limit_ms or settings.DEFAULT_TIME_LIMIT_MS,
                memory_limit_mb=problem.memory_limit_mb or settings.DEFAULT_MEMORY_LIMIT_MB,
                output_limit_kb=problem.output_limit_kb or settings.DEFAULT_OUTPUT_LIMIT_KB
            )
            
            # Track stats
            total_time += exec_result.time_ms
            max_memory = max(max_memory, exec_result.memory_kb)
            
            # Check for execution errors first
            if exec_result.verdict != "OK":
                verdict = exec_result.verdict
            else:
                # Check output correctness
                checker_result, message = Checker.check_output(
                    checker_type=problem.checker_type.value,
                    expected=testcase.output_blob,
                    actual=exec_result.output
                )
                
                if checker_result == CheckerResult.AC:
                    verdict = "AC"
                else:
                    verdict = "WA"
            
            # Store test result
            test_result = {
                "test_id": testcase.id,
                "verdict": verdict,
                "time_ms": exec_result.time_ms,
                "memory_kb": exec_result.memory_kb,
                "input_preview": testcase.input_blob[:100] + "..." if len(testcase.input_blob) > 100 else testcase.input_blob,
                "output_preview": exec_result.output[:100] + "..." if len(exec_result.output) > 100 else exec_result.output,
                "expected_preview": testcase.output_blob[:100] + "..." if len(testcase.output_blob) > 100 else testcase.output_blob
            }
            results.append(test_result)
            
            # Update overall verdict
            if verdict != "AC":
                if overall_verdict == SubmissionVerdict.AC:
                    overall_verdict = SubmissionVerdict(verdict.lower())
                    first_failed_test = i + 1
                
                # Stop on first failure for most verdicts (except WA, where we might want to run all tests)
                if verdict in ["TLE", "MLE", "RE", "CE", "OLE"]:
                    break
        
        # Update submission with results
        submission.verdict = overall_verdict
        submission.time_ms = total_time
        submission.memory_kb = max_memory
        submission.first_failed_test = first_failed_test
        submission.test_results = results
        submission.judged_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(
            "Judging completed",
            submission_id=submission_id,
            verdict=overall_verdict.value,
            time_ms=total_time,
            memory_kb=max_memory,
            tests_run=len(results)
        )
        
        # TODO: Update gamification profile if AC
        
        return {
            "submission_id": submission_id,
            "verdict": overall_verdict.value,
            "time_ms": total_time,
            "memory_kb": max_memory,
            "tests_run": len(results),
            "first_failed_test": first_failed_test
        }
        
    except Exception as e:
        logger.error("Judging failed", submission_id=submission_id, error=str(e))
        
        # Mark submission as system error
        try:
            submission = db.query(Submission).filter(Submission.id == submission_id).first()
            if submission:
                submission.verdict = SubmissionVerdict.RE
                submission.judged_at = datetime.utcnow()
                db.commit()
        except Exception:
            pass
        
        raise e
    
    finally:
        db.close()


def _store_source_code(submission_id: int, source_code: str) -> str:
    """Store source code and return reference."""
    import hashlib
    
    # Create artifacts directory if it doesn't exist
    artifacts_dir = "/judge_artifacts"
    os.makedirs(artifacts_dir, exist_ok=True)
    
    # Generate hash-based filename
    code_hash = hashlib.sha256(source_code.encode()).hexdigest()[:16]
    filename = f"{submission_id}_{code_hash}.txt"
    filepath = os.path.join(artifacts_dir, filename)
    
    # Write source code to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(source_code)
    
    return filename