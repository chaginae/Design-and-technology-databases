from django.contrib.auth.models import User
from django.db import models


class Employee(models.Model):
    TYPE_TECHNICIAN = "техник"
    TYPE_ENGINEER = "инженер"
    TYPE_DEVELOPER = "разработчик"
    EMPLOYEE_TYPE_CHOICES = (
        (TYPE_TECHNICIAN, "Техник"),
        (TYPE_ENGINEER, "Инженер"),
        (TYPE_DEVELOPER, "Разработчик"),
    )

    INSTITUTE_HSE = "НИУ ВШЭ"
    INSTITUTE_MIPT = "МФТИ"
    INSTITUTE_BAUMAN = "Дауманка"
    INSTITUTE_CHOICES = (
        (INSTITUTE_HSE, "НИУ ВШЭ"),
        (INSTITUTE_MIPT, "МФТИ"),
        (INSTITUTE_BAUMAN, "Дауманка"),
    )

    LANG_PYTHON = "Python"
    LANG_CPP = "C/C++"
    LANG_RUST = "Rust"
    LANG_GO = "Go"
    PROGRAMMING_LANGUAGE_CHOICES = (
        (LANG_PYTHON, "Python"),
        (LANG_CPP, "C/C++"),
        (LANG_RUST, "Rust"),
        (LANG_GO, "Go"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    position = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)

    employee_type = models.CharField(
        max_length=20,
        choices=EMPLOYEE_TYPE_CHOICES,
        blank=True,
    )
    tech_department = models.CharField(max_length=100, blank=True)
    tech_rank = models.CharField(max_length=50, blank=True)
    institute = models.CharField(
        max_length=50,
        choices=INSTITUTE_CHOICES,
        blank=True,
    )
    programming_language = models.CharField(
        max_length=20,
        choices=PROGRAMMING_LANGUAGE_CHOICES,
        blank=True,
    )
    specialization = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name}"
