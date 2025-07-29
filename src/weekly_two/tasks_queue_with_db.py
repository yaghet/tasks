from typing import Optional
from django.db import models, transaction


class TaskQueue(models.Model):
    task_name = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.task_name


def fetch_task() -> Optional[TaskQueue]:
    with transaction.atomic():
        task: TaskQueue | None = (
            TaskQueue.objects.select_for_update(skip_locked=True)
            .filter(status="pending")
            .first()
        )
        if not task:
            return None
        task.status = "in_process"
        return task


if __name__ == "__main__":
    fetch_task()
