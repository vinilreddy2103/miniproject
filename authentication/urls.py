from django.urls import path
from . import views

urlpatterns = [
    # Authentication Routes
    path("", views.login, name="login"),  # Root URL (default to login)
    path("signup/", views.signup, name="signup"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),

    # Home Page
    path("home/", views.home, name="home"),

    # Habit Tracker APIs
    path("api/user-habits/", views.get_user_habits, name="get-user-habits"),
    path("api/add-habit/", views.add_habit, name="add-habit"),
    path("api/update-habit/<int:habit_id>/", views.update_habit, name="update-habit"),
]
