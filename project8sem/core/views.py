from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView

from .models import Employee


class UserLoginView(View):
    template_name = "core/login.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""
        if not username or not password:
            return render(
                request,
                self.template_name,
                {"error": "Введите логин и пароль."},
            )
        user = authenticate(
            request,
            username=username,
            password=password,
        )
        if user is not None:
            login(request, user)
            # Пример работы с сессией
            request.session["user_id"] = user.id
            request.session["username"] = user.username
            return redirect("employees")

        return render(
            request,
            self.template_name,
            {"error": "Неверный логин или пароль"},
        )


class UserLogoutView(View):
    """Выход из системы. Редирект на страницу входа."""

    def get(self, request):
        logout(request)
        return redirect("login")


class UserRegisterView(View):
    template_name = "core/register.html"
    success_url = reverse_lazy("login")
    gender_choices = ("Мужской", "Женский")
    required_fields = (
        ("username", "Логин"),
        ("password", "Пароль"),
        ("password_confirm", "Подтверждение пароля"),
        ("first_name", "Имя"),
        ("last_name", "Фамилия"),
        ("position", "Должность"),
        ("department", "Подразделение"),
    )

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("employees")
        return render(
            request,
            self.template_name,
            {"gender_choices": self.gender_choices},
        )

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("employees")

        errors = []
        post = request.POST

        for field_name, label in self.required_fields:
            raw = post.get(field_name) or ""
            value = raw.strip() if field_name not in ("password", "password_confirm") else raw
            if not value:
                errors.append(f"Заполните поле «{label}».")

        if post.get("password") != post.get("password_confirm"):
            errors.append("Пароли не совпадают.")

        date_of_birth = None
        raw_date = (post.get("date_of_birth") or "").strip()
        if raw_date:
            try:
                date_of_birth = datetime.strptime(raw_date, "%d.%m.%Y").date()
            except ValueError:
                errors.append("Неверный формат даты. Используйте ДД.ММ.ГГГГ.")

        raw_gender = (post.get("gender") or "").strip()
        if raw_gender and raw_gender not in self.gender_choices:
            errors.append("Укажите пол: Мужской или Женский.")
        gender_value = raw_gender if raw_gender in self.gender_choices else ""

        if errors:
            return render(
                request,
                self.template_name,
                {"errors": errors, "gender_choices": self.gender_choices},
            )

        user = User.objects.create_user(
            username=post.get("username").strip(),
            password=post.get("password"),
            first_name=post.get("first_name").strip(),
            last_name=post.get("last_name").strip(),
        )

        Employee.objects.create(
            user=user,
            position=post.get("position").strip(),
            department=post.get("department").strip(),
            date_of_birth=date_of_birth,
            gender=gender_value,
        )

        return redirect(self.success_url)


class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = "core/employees.html"
    context_object_name = "employees"
    login_url = reverse_lazy("login")

    def get_queryset(self):
        return Employee.objects.select_related("user")
