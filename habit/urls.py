from django.urls import path
from . import views

urlpatterns = [
    path("home/", views.home, name="home"),
    path("api/user-habits/", views.get_user_habits, name="get-user-habits"),
    path("api/add-habit/", views.add_habit, name="add-habit"),
    path("api/update-habit/<int:habit_id>/", views.update_habit, name="update-habit"),
    path("api/delete-habit/<int:habit_id>/", views.delete_habit, name="delete-habit"),
    path("api/increment-habit/<int:habit_id>/", views.increment_habit, name="increment-habit"),
    path("api/complete-habit/<int:habit_id>/", views.complete_habit, name="complete-habit"),
]
