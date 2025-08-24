import os
import sys
from celery import Celery
from dotenv import load_dotenv
from tasks import judge_submission

# Load environment variables
load_dotenv()

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Create Celery app
app = Celery('judgelab-worker')

# Configure Celery
app.conf.update(
    broker_url=os.getenv('REDIS_URL', 'redis://localhost:6379'),
    result_backend=os.getenv('REDIS_URL', 'redis://localhost:6379'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_max_tasks_per_child=50,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Register tasks
app.task(judge_submission.judge_submission)

if __name__ == '__main__':
    app.start()