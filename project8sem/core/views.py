from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView

from .models import Employee

EMPLOYEE_TYPE_CHOICES = (
    (Employee.TYPE_TECHNICIAN, "Техник"),
    (Employee.TYPE_ENGINEER, "Инженер"),
    (Employee.TYPE_DEVELOPER, "Разработчик"),
)
INSTITUTE_CHOICES = Employee.INSTITUTE_CHOICES
PROGRAMMING_LANGUAGE_CHOICES = Employee.PROGRAMMING_LANGUAGE_CHOICES


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
    valid_employee_types = (
        Employee.TYPE_TECHNICIAN,
        Employee.TYPE_ENGINEER,
        Employee.TYPE_DEVELOPER,
    )

    def _get_context(self, request, errors=None, post_data=None):
        gender_choices = self.gender_choices
        if request.method == "GET":
            employee_type = (request.GET.get("employee_type") or "").strip()
        else:
            employee_type = (post_data or {}).get("employee_type") or ""
        if employee_type not in self.valid_employee_types:
            employee_type = ""
        return {
            "gender_choices": gender_choices,
            "employee_type_choices": EMPLOYEE_TYPE_CHOICES,
            "institute_choices": INSTITUTE_CHOICES,
            "programming_language_choices": PROGRAMMING_LANGUAGE_CHOICES,
            "employee_type": employee_type,
            "errors": errors,
            "post_data": post_data or {},
        }

    def _validate_required_fields(self, post, errors):
        for field_name, label in self.required_fields:
            raw = post.get(field_name) or ""
            value = raw.strip() if field_name not in ("password", "password_confirm") else raw
            if not value:
                errors.append(f"Заполните поле «{label}».")

    def _validate_employee_type_fields(self, post, errors):
        employee_type = (post.get("employee_type") or "").strip()
        if not employee_type:
            errors.append("Выберите тип сотрудника.")
            return None
        if employee_type not in self.valid_employee_types:
            errors.append("Укажите тип сотрудника: техник, инженер или разработчик.")
            return None
        if employee_type == Employee.TYPE_TECHNICIAN:
            self._validate_technician_fields(post, errors)
        elif employee_type == Employee.TYPE_ENGINEER:
            self._validate_engineer_fields(post, errors)
        elif employee_type == Employee.TYPE_DEVELOPER:
            self._validate_developer_fields(post, errors)
        return employee_type

    def _validate_technician_fields(self, post, errors):
        if not (post.get("tech_department") or "").strip():
            errors.append("Заполните поле «Отдел».")
        if not (post.get("tech_rank") or "").strip():
            errors.append("Заполните поле «Разряд».")

    def _validate_engineer_fields(self, post, errors):
        inst = (post.get("institute") or "").strip()
        valid_institutes = [c[0] for c in INSTITUTE_CHOICES]
        if not inst:
            errors.append("Выберите институт.")
        elif inst not in valid_institutes:
            errors.append("Укажите институт: НИУ ВШЭ, МФТИ или Дауманка.")

    def _validate_developer_fields(self, post, errors):
        lang = (post.get("programming_language") or "").strip()
        spec = (post.get("specialization") or "").strip()
        valid_langs = [c[0] for c in PROGRAMMING_LANGUAGE_CHOICES]
        if not lang:
            errors.append("Выберите язык программирования.")
        elif lang not in valid_langs:
            errors.append("Укажите язык программирования из списка.")
        if not spec:
            errors.append("Заполните поле «Специализация».")

    def _validate_password(self, post, errors):
        password = post.get("password") or ""
        if password and len(password) < 8:
            errors.append("Пароль должен содержать не менее 8 символов.")
        if post.get("password") != post.get("password_confirm"):
            errors.append("Пароли не совпадают.")

    def _parse_date_and_gender(self, post, errors):
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
        return date_of_birth, gender_value

    def _extract_extra_fields(self, post, employee_type):
        if employee_type == Employee.TYPE_TECHNICIAN:
            return {
                "tech_department": (post.get("tech_department") or "").strip(),
                "tech_rank": (post.get("tech_rank") or "").strip(),
                "institute": "",
                "programming_language": "",
                "specialization": "",
            }
        if employee_type == Employee.TYPE_ENGINEER:
            return {
                "tech_department": "",
                "tech_rank": "",
                "institute": (post.get("institute") or "").strip(),
                "programming_language": "",
                "specialization": "",
            }
        if employee_type == Employee.TYPE_DEVELOPER:
            return {
                "tech_department": "",
                "tech_rank": "",
                "institute": "",
                "programming_language": (post.get("programming_language") or "").strip(),
                "specialization": (post.get("specialization") or "").strip(),
            }
        return {
            "tech_department": "",
            "tech_rank": "",
            "institute": "",
            "programming_language": "",
            "specialization": "",
        }

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("employees")
        context = self._get_context(request)
        return render(request, self.template_name, context)

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("employees")

        post = request.POST
        errors = []

        self._validate_required_fields(post, errors)
        employee_type = self._validate_employee_type_fields(post, errors)
        self._validate_password(post, errors)
        date_of_birth, gender_value = self._parse_date_and_gender(post, errors)

        if errors:
            context = self._get_context(request, errors=errors, post_data=post)
            return render(request, self.template_name, context)

        user = User.objects.create_user(
            username=post.get("username").strip(),
            password=post.get("password"),
            first_name=post.get("first_name").strip(),
            last_name=post.get("last_name").strip(),
        )
        extra = self._extract_extra_fields(post, employee_type)
        Employee.objects.create(
            user=user,
            position=post.get("position").strip(),
            department=post.get("department").strip(),
            date_of_birth=date_of_birth,
            gender=gender_value,
            employee_type=employee_type,
            tech_department=extra["tech_department"],
            tech_rank=extra["tech_rank"],
            institute=extra["institute"],
            programming_language=extra["programming_language"],
            specialization=extra["specialization"],
        )
        return redirect(self.success_url)


class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = "core/employees.html"
    context_object_name = "employees"
    login_url = reverse_lazy("login")

    def get_queryset(self):
        return Employee.objects.select_related("user")
