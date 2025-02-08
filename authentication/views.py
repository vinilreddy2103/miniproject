from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from authentication.models import CustomUser, Habit  # Import models
import json
from datetime import date
from django.http import JsonResponse


# ✅ SIGNUP VIEW
def signup(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not username or not email or not password:
            messages.error(request, "All fields are required.")
            return render(request, "signup.html")

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, "signup.html")

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, "signup.html")

        # Create the user
        user = CustomUser.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created successfully. Please log in.")
        return redirect("login")

    return render(request, "signup.html")


# ✅ LOGIN VIEW
def login(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, "Login successful!")

            next_url = request.GET.get("next")
            return redirect(next_url if next_url else "home")

        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "login.html")


# ✅ HOME VIEW (SHOW USER'S HABITS)
@login_required
def home(request):
    return render(request, "home.html")


# ✅ LOGOUT VIEW
def logout(request):
    auth_logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")


# ✅ API: GET USER HABITS
@login_required
def get_user_habits(request):
    """Fetch all habits for the logged-in user"""
    habits = Habit.objects.filter(user=request.user, date=date.today())  # Get today's habits
    habits_list = [
        {
            "id": habit.id,
            "name": habit.name,
            "habit_type": habit.habit_type,
            "current_count": habit.current_count,
            "target_count": habit.target_count,
            "completed": habit.completed,
        }
        for habit in habits
    ]
    return JsonResponse({"habits": habits_list})


# ✅ API: ADD NEW HABIT
@csrf_exempt
@login_required
def add_habit(request):
    """Create a new habit"""
    if request.method == "POST":
        data = json.loads(request.body)
        habit_name = data.get("name")
        habit_type = data.get("habit_type")
        target_count = data.get("target_count", 1)  # Default target count = 1
        current_count = 0  # Start with 0 progress

        if not habit_name or habit_type not in ["measurable", "non-measurable"]:
            return JsonResponse({"error": "Invalid habit data"}, status=400)

        habit = Habit.objects.create(
            user=request.user,
            name=habit_name,
            habit_type=habit_type,
            target_count=target_count,
            current_count=current_count,
            completed=False  # New habits are not completed yet
        )
        return JsonResponse({"message": "Habit added successfully!", "id": habit.id}, status=201)


# ✅ API: UPDATE HABIT STATUS / PROGRESS
@csrf_exempt
@login_required
def update_habit(request, habit_id):
    """Update completion status or progress count"""
    try:
        habit = Habit.objects.get(id=habit_id, user=request.user)
    except Habit.DoesNotExist:
        return JsonResponse({"error": "Habit not found"}, status=404)

    if request.method == "POST":
        data = json.loads(request.body)

        # ✅ Update measurable habits (increment progress)
        if "current_count" in data and habit.habit_type == "measurable":
            habit.current_count = data["current_count"]
            habit.completed = habit.current_count >= habit.target_count  # Auto-complete when target reached

        # ✅ Update non-measurable habits
        if "completed" in data:
            habit.completed = data["completed"]

        habit.save()
        return JsonResponse({"message": "Habit updated successfully!"})


# ✅ API: RESET HABITS DAILY
def reset_habits():
    """Every day at 12 AM, reset habits to undone"""
    Habit.objects.all().update(current_count=0, completed=False)
    print("✅ Daily habit reset completed.")
