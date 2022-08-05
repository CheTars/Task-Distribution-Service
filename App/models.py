from django.db import models
from django.contrib.auth.models import AbstractUser


## CHOICES ##


class UserStatus(models.TextChoices):
    IN_TEAM = "In team"
    BENCH = "Bench"
    FIRED = "Fired"


class Role(models.TextChoices):
    WORKER = "Worker"
    MANAGER = "Manager"
    ADMIN = "Admin"


class TaskStatus(models.TextChoices):
    BACKLOG = "Backlog"
    READY_TO_DEV = "Ready to development"
    IN_PROGRESS = "In progress"
    READY_TO_QA = "Ready to Quality Assurance"
    PRODUCTION = "Production"


## MODELS ##

class CustomUser(AbstractUser):
    status = models.CharField(max_length=7, choices=UserStatus.choices, default=UserStatus.BENCH)
    role = models.CharField(max_length=7, choices=Role.choices, default=Role.WORKER)
    team = models.ForeignKey('Team', on_delete=models.SET_NULL, related_name='team_members', null=True, blank=True)

    def set_status(self):
        in_team = bool(self.team)
        fired = self.status == UserStatus.FIRED
        if fired:
            self.team = None
            return
        statuses = {
            True: UserStatus.IN_TEAM,
            False: UserStatus.BENCH
        }
        self.status = statuses[in_team]

    def save(self, *args, **kwargs):
        self.set_status()
        return super().save(*args, **kwargs)

    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"


class Team(models.Model):
    team_name = models.CharField(max_length=255)

    # workers = models.ManyToManyField(CustomUser, related_name='team_workers', limit_choices_to={
    #     "worker_status": UserStatus.BENCH,
    #     "role": Role.WORKER,
    # },
    #                                  null=True,
    #                                  blank=True)

    managers = models.ForeignKey(CustomUser, related_name='team_managers', limit_choices_to={"role": Role.MANAGER},
                                 null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.team_name

    @property
    def workers_count(self):
        return self.team_members.count()

    # secret_token_key


class TaskImage(models.Model):
    image = models.ImageField()


class Task(models.Model):
    task_name = models.CharField(max_length=255)
    description = models.TextField()
    connection_with_another_task = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField()
    task_status = models.CharField(max_length=26, choices=TaskStatus.choices, default=TaskStatus.BACKLOG)
    image = models.ManyToManyField(TaskImage)
    responsible_team = models.ForeignKey(Team, related_name='tasks_team', on_delete=models.CASCADE)
    responsible_employee = models.ForeignKey(CustomUser, related_name='task_employee', blank=True, on_delete=models.CASCADE)

    @property
    def comments_count(self):
        return self.comments.count()


class TaskComment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='TaskComments')
    text = models.TextField(max_length=2550)
