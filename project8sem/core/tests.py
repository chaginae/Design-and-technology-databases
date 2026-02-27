from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import Employee


class EmployeeModelTests(TestCase):
    def test_employee_str(self):
        user = User.objects.create_user(
            username="ivan",
            first_name="Иван",
            last_name="Иванов",
            password="12345",
        )
        employee = Employee.objects.create(
            user=user,
            position="Инженер",
            department="АСУ ТП",
        )
        self.assertEqual(str(employee), "Иванов Иван")


class RegisterViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Создаём пользователя для тестов авторизации
        self.user = User.objects.create_user(
            username="existing_user",
            password="12345",
        )

    def test_register_page_available(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/register.html")

    def test_register_creates_user_and_employee(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "petrov",
                "password": "12345",
                "password_confirm": "12345",
                "first_name": "Петр",
                "last_name": "Петров",
                "position": "Оператор",
                "department": "Цех 1",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username="petrov").exists())
        self.assertTrue(Employee.objects.filter(user__username="petrov").exists())

    def test_register_password_mismatch_stays_on_page(self):
        """При несовпадении паролей пользователь остаётся на странице регистрации."""
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "password": "12345",
                "password_confirm": "54321",
                "first_name": "Иван",
                "last_name": "Иванов",
                "position": "Инженер",
                "department": "Цех 1",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/register.html")
        self.assertFalse(User.objects.filter(username="newuser").exists())

    def test_register_password_mismatch_shows_error(self):
        """При несовпадении паролей отображается сообщение об ошибке."""
        response = self.client.post(
            reverse("register"),
            {
                "username": "u",
                "password": "a",
                "password_confirm": "b",
                "first_name": "",
                "last_name": "",
                "position": "",
                "department": "",
            },
        )
        self.assertContains(response, "Пароли не совпадают")

    def test_register_saves_date_of_birth_and_gender(self):
        """Регистрация сохраняет дату рождения и пол в профиле сотрудника."""
        self.client.post(
            reverse("register"),
            {
                "username": "sidorov",
                "password": "12345",
                "password_confirm": "12345",
                "first_name": "Сидор",
                "last_name": "Сидоров",
                "date_of_birth": "15.03.1990",
                "gender": "Мужской",
                "position": "Техник",
                "department": "ОТК",
            },
            follow=True,
        )
        emp = Employee.objects.get(user__username="sidorov")
        self.assertEqual(emp.date_of_birth.year, 1990)
        self.assertEqual(emp.date_of_birth.month, 3)
        self.assertEqual(emp.date_of_birth.day, 15)
        self.assertEqual(emp.gender, "Мужской")

    def test_register_invalid_date_shows_error(self):
        """При неверном формате даты отображается сообщение об ошибке."""
        response = self.client.post(
            reverse("register"),
            {
                "username": "u",
                "password": "12345",
                "password_confirm": "12345",
                "first_name": "А",
                "last_name": "Б",
                "date_of_birth": "31.13.2000",
                "gender": "",
                "position": "П",
                "department": "Д",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Неверный формат даты")
        self.assertFalse(User.objects.filter(username="u").exists())

    def test_register_invalid_gender_shows_error(self):
        """При недопустимом значении пола отображается сообщение об ошибке."""
        response = self.client.post(
            reverse("register"),
            {
                "username": "u",
                "password": "12345",
                "password_confirm": "12345",
                "first_name": "А",
                "last_name": "Б",
                "date_of_birth": "",
                "gender": "Неизвестно",
                "position": "П",
                "department": "Д",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Укажите пол")
        self.assertFalse(User.objects.filter(username="u").exists())

    def test_register_empty_required_fields_shows_errors(self):
        """При пустых обязательных полях отображаются сообщения об ошибках,
        пользователь не создаётся."""
        initial_count = User.objects.count()
        response = self.client.post(
            reverse("register"),
            {
                "username": "",
                "password": "",
                "password_confirm": "",
                "first_name": "",
                "last_name": "",
                "date_of_birth": "",
                "gender": "",
                "position": "",
                "department": "",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Заполните поле")
        self.assertEqual(User.objects.count(), initial_count)

    def test_register_redirect_if_authenticated(self):
        """Авторизованные пользователи при GET /register/ перенаправляются на основной раздел."""
        self.client.login(username="existing_user", password="12345")
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("employees"))


class LoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="admin",
            password="12345",
        )

    def test_login_page_available(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/login.html")

    def test_login_success_redirects(self):
        response = self.client.post(
            reverse("login"),
            {"username": "admin", "password": "12345"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("employees"), response.url)

    def test_login_fail_stays_on_page(self):
        response = self.client.post(
            reverse("login"),
            {"username": "admin", "password": "wrong"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/login.html")

    def test_login_empty_credentials_shows_error(self):
        """При пустых логине и пароле отображается сообщение об ошибке."""
        response = self.client.post(
            reverse("login"),
            {"username": "", "password": ""},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Введите логин и пароль")


class LogoutViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="logout_user",
            password="12345",
        )

    def test_logout_redirects_to_login(self):
        """После выхода пользователь перенаправляется на страницу входа."""
        self.client.login(username="logout_user", password="12345")
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login"))

    def test_after_logout_user_not_authenticated(self):
        """После выхода запрос от того же клиента идёт без авторизации."""
        self.client.login(username="logout_user", password="12345")
        self.client.get(reverse("logout"))
        response = self.client.get(reverse("employees"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_logout_button_visible_when_authenticated(self):
        """На странице сотрудников у авторизованного пользователя есть кнопка Выход."""
        self.client.login(username="logout_user", password="12345")
        response = self.client.get(reverse("employees"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Выход")
        self.assertContains(response, reverse("logout"))


class EmployeesViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="user",
            password="12345",
            first_name="Иван",
            last_name="Иванов",
        )
        self.employee = Employee.objects.create(
            user=self.user,
            position="Инженер",
            department="АСУ ТП",
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("employees"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_logged_in_user_can_see_employees(self):
        self.client.login(username="user", password="12345")
        response = self.client.get(reverse("employees"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/employees.html")
        self.assertContains(response, "Инженер")
        self.assertContains(response, "АСУ ТП")
        self.assertContains(response, "Иванов")

    def test_employees_queryset_not_empty(self):
        self.client.login(username="user", password="12345")
        response = self.client.get(reverse("employees"))
        self.assertTrue(len(response.context["employees"]) > 0)
