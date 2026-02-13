from django.urls import path

from .views import EmployeeListView, UserLoginView, UserLogoutView, UserRegisterView

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("register/", UserRegisterView.as_view(), name="register"),
    path("employees/", EmployeeListView.as_view(), name="employees"),
]
