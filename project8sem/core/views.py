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
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
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

        if request.POST.get("password") != request.POST.get("password_confirm"):
            return render(
                request,
                self.template_name,
                {"error": "Пароли не совпадают.", "gender_choices": self.gender_choices},
            )

        date_of_birth = None
        raw_date = (request.POST.get("date_of_birth") or "").strip()
        if raw_date:
            try:
                date_of_birth = datetime.strptime(
                    raw_date, "%d.%m.%Y"
                ).date()
            except ValueError:
                return render(
                    request,
                    self.template_name,
                    {
                        "error": "Неверный формат даты. Используйте ДД.ММ.ГГГГ.",
                        "gender_choices": self.gender_choices,
                    },
                )

        raw_gender = (request.POST.get("gender") or "").strip()
        if raw_gender and raw_gender not in self.gender_choices:
            return render(
                request,
                self.template_name,
                {
                    "error": "Укажите пол: Мужской или Женский.",
                    "gender_choices": self.gender_choices,
                },
            )
        gender_value = raw_gender if raw_gender in self.gender_choices else ""

        user = User.objects.create_user(
            username=request.POST.get("username"),
            password=request.POST.get("password"),
            first_name=request.POST.get("first_name"),
            last_name=request.POST.get("last_name"),
        )

        Employee.objects.create(
            user=user,
            position=request.POST.get("position"),
            department=request.POST.get("department"),
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
