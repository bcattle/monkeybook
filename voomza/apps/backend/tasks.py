from celery import task
from voomza.apps.backend.pipeline.yearbook import YearbookTaskPipeline


@task.task()
def run_yearbook(user):
    pipeline = YearbookTaskPipeline(user)
    # Perform all the I/O intensive operations
    results = pipeline.run()

    # Perform the (minimally) CPU-intensive operations
    # aka sorting lists of a thousand elements

    # Sort for top photos of year
    # Sort for top photos of first half of year
    # Sort for top photos of second half of year
    # Sort for top photos back in time

    # Look for same groups back in time

    # Save everything to the db
