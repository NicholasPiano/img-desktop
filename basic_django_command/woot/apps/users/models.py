# woot.apps.users.models

# django
from django.db import models
from django.contrib.auth.models import (
  BaseUserManager, AbstractBaseUser, PermissionsMixin
)

# local

# vars

# classes
class UserManager(BaseUserManager):
  def create_user(self, username, email, password=None):
    """
    Creates and saves a User with the given email, date of
    birth and password.
    """
    if not email:
        raise ValueError('Users must have an email address')

    user = self.model(username,
        email=self.normalize_email(email),
    )

    user.set_password(password)
    user.save(using=self._db)
    return user

  def create_superuser(self, username, email, password):
    """
    Creates and saves a superuser with the given email, date of
    birth and password.
    """
    user = self.create_user(username, email,
      password=password,
    )
    user.is_admin = True
    user.save(using=self._db)
    return user

class User(AbstractBaseUser, PermissionsMixin):
  # properties
  username = models.CharField(max_length=255)
  email = models.EmailField(verbose_name='email address',max_length=255,unique=True)
  is_active = models.BooleanField(default=True)
  is_admin = models.BooleanField(default=False)
  objects = UserManager()

  USERNAME_FIELD = 'username'
  REQUIRED_FIELDS = ['username']

  # methods
  def get_full_name(self):
    # The user is identified by their email address
    return self.username

  def get_short_name(self):
    # The user is identified by their email address
    return self.username

  def __str__(self):
    return '{}: {}'.format(self.username, self.email)

  def has_perm(self, perm, obj=None):
    "Does the user have a specific permission?"
    # Simplest possible answer: Yes, always
    return True

  def has_module_perms(self, app_label):
    "Does the user have permissions to view the app `app_label`?"
    # Simplest possible answer: Yes, always
    return True

  @property
  def is_staff(self):
    "Is the user a member of staff?"
    # Simplest possible answer: All admins are staff
    return self.is_admin
