from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.validators import MinValueValidator


class UserManager(BaseUserManager):
    def create_user(self, email, name, age, password=None, role=None):
        """
        Creates and saves a User with the given email, name, age
        and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        if role not in [User.Role.ADMIN, User.Role.EMPLOYEE, User.Role.CUSTOMER]:
            raise ValueError("Invalid role")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            age=age,
            role=role,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, age, password=None):
        """
        Creates and saves a superuser with the given email, name, age and password.
        """
        user = self.create_user(
            email, name=name, age=age, password=password, role=User.Role.ADMIN
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

    def create_employee(self, email, name, age, password=None):
        """
        Creates and saves an employee.
        """
        return self.create_user(
            email=email, name=name, age=age, password=password, role=User.Role.EMPLOYEE
        )

    def create_customer(self, email, name, age, password=None):
        """
        Creates and saves a customer.
        """
        return self.create_user(
            email=email, name=name, age=age, password=password, role=User.Role.CUSTOMER
        )


class User(AbstractBaseUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        EMPLOYEE = "EMPLOYEE", "Employee"
        CUSTOMER = "CUSTOMER", "Customer"

    email = models.EmailField(
        verbose_name="Email",
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=255)
    age = models.IntegerField(validators=[MinValueValidator(18)])
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.CUSTOMER)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "age"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        if self.role == self.Role.ADMIN:
            return True
        return False

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        if self.role == self.Role.ADMIN:
            return True
        return False

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        # Simplest possible answer: All admins are staff
        return self.role in {self.Role.ADMIN}
