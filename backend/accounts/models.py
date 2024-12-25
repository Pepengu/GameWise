from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError("The Email field must be set")
        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        user = self.create_user(username, email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    profile_photo = models.ImageField(
        upload_to="profile_photos/", blank=True, null=True
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.username

    def has_perm(self, a):
        return self.is_superuser

    def has_module_perms(self, a):
        return self.is_superuser


class Course(models.Model):
    title = models.CharField(max_length=255, unique=True, verbose_name="Название")
    author = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True
    )
    description = models.TextField(max_length=500, verbose_name="Описание")
    tags = models.CharField(max_length=255, verbose_name="Тематика")
    content = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="enrollments"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments"
    )
    enrollment_date = models.DateField(
        auto_now_add=True, verbose_name="Дата записи", null=True, blank=True
    )


class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="questions")
    text = models.CharField(max_length=255)


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)


class QuizResult(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    correct_answers = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.course.title} - {self.score}%"
