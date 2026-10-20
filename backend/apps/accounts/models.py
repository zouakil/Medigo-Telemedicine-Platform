import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email obligatoire')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('medecin', 'Médecin'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    est_actif = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    @property
    def is_active(self):
        """Use the application's activation flag in Django authentication."""
        return self.est_actif

    @is_active.setter
    def is_active(self, value):
        self.est_actif = value

    class Meta:
        db_table = 'user'
        verbose_name = 'Utilisateur'

    def __str__(self):
        return self.email


class MedecinProfile(models.Model):
    STATUT_CHOICES = [
        ('disponible', 'Disponible'),
        ('indisponible', 'Indisponible'),
        ('occupe', 'Occupé'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='medecin_profile')
    cree_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='medecins_crees')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    specialite = models.CharField(max_length=100)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='indisponible')

    class Meta:
        db_table = 'medecin_profile'
        verbose_name = 'Profil médecin'

    def __str__(self):
        return f"Dr. {self.prenom} {self.nom}"
