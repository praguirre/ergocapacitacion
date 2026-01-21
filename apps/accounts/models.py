from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


class TraineeUserManager(BaseUserManager):
    def create_user(self, cuil: str, email: str, **extra_fields):
        if not cuil:
            raise ValueError("CUIL es requerido")
        if not email:
            raise ValueError("Email es requerido")

        email = self.normalize_email(email)
        user = self.model(cuil=cuil, email=email, **extra_fields)
        user.set_unusable_password()  # sin password por defecto (flujo real en Commit 2)
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, cuil: str, email: str, password: str, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        user = self.model(cuil=cuil, email=self.normalize_email(email), **extra_fields)
        user.set_password(password)  # superuser sí tiene password
        user.is_active = True
        user.save(using=self._db)
        return user


class TraineeUser(AbstractBaseUser, PermissionsMixin):
    cuil = models.CharField(max_length=20, unique=True, db_index=True)
    email = models.EmailField(unique=True, db_index=True)

    full_name = models.CharField(max_length=200, blank=True, default="")
    job_title = models.CharField(max_length=200, blank=True, default="")
    company_name = models.CharField(max_length=200, blank=True, default="")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = TraineeUserManager()

    USERNAME_FIELD = "cuil"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return f"{self.full_name or self.email} ({self.cuil})"
