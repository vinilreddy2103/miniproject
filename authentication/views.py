from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from authentication.models import CustomUser, Habit
import json

def signup(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not username or not email or not password:
            return JsonResponse({"error": "All fields are required."}, status=400)

        if CustomUser.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already taken."}, status=400)

        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email already registered."}, status=400)

        CustomUser.objects.create_user(username=username, email=email, password=password)
        return JsonResponse({"message": "Account created successfully!", "redirect": "/login/"}, status=201)

    return render(request, "signup.html")


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


@login_required
def home(request):
    return render(request, "home.html")


def logout(request):
    auth_logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")


@login_required
def get_user_habits(request):
    habits = Habit.objects.filter(user=request.user).order_by("completed", "id")
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


@csrf_exempt
@login_required
def add_habit(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            habit_name = data.get("name")
            habit_type = data.get("habit_type")
            target_count = int(data.get("target_count", 1))  # Ensure it's an integer
            current_count = 0

            if not habit_name or habit_type not in ["measurable", "non-measurable"]:
                return JsonResponse({"error": "Invalid habit data"}, status=400)

            habit = Habit.objects.create(
                user=request.user,
                name=habit_name,
                habit_type=habit_type,
                target_count=target_count,
                current_count=current_count,
                completed=False
            )
            return JsonResponse({"message": "Habit added successfully!", "id": habit.id}, status=201)

        except (json.JSONDecodeError, ValueError) as e:
            print("Error in add_habit:", str(e))  # Debugging line
            return JsonResponse({"error": "Invalid JSON data"}, status=400)


@csrf_exempt
@login_required
def update_habit(request, habit_id):
    try:
        habit = Habit.objects.get(id=habit_id)

        if request.method == "PUT":
            data = json.loads(request.body)
            
            # Update fields if they exist in request
            habit.name = data.get("name", habit.name)
            habit.habit_type = data.get("habit_type", habit.habit_type)
            habit.target_count = data.get("target_count", habit.target_count)

            habit.save()

            return JsonResponse({"message": "Habit updated successfully"}, status=200)
        
        elif request.method == "POST":
            data = json.loads(request.body)
            
            if "current_count" in data and data["current_count"] == "increment":
                habit.current_count += 1
                if habit.current_count >= habit.target_count:
                    habit.completed = True
                habit.save()
                return JsonResponse({"message": "Habit incremented", "new_progress": habit.current_count, "target": habit.target_count}, status=200)

            elif "completed" in data:
                habit.completed = data["completed"]
                habit.save()
                return JsonResponse({"message": "Habit completion status updated"}, status=200)

        # If the request method is not handled, return an error
        return JsonResponse({"error": "Invalid request method"}, status=400)
    
    except Habit.DoesNotExist:
        return JsonResponse({"error": "Habit not found"}, status=404)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)

    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)



@csrf_exempt
@login_required
def delete_habit(request, habit_id):
    try:
        habit = Habit.objects.get(id=habit_id, user=request.user)
    except Habit.DoesNotExist:
        return JsonResponse({"error": "Habit not found"}, status=404)

    if request.method == "DELETE":
        habit.delete()
        return JsonResponse({"message": "Habit deleted successfully!"})


@csrf_exempt
@login_required
def increment_habit(request, habit_id):
    try:
        habit = Habit.objects.get(id=habit_id, user=request.user)
    except Habit.DoesNotExist:
        return JsonResponse({"error": "Habit not found"}, status=404)

    if request.method == "POST":
        if habit.habit_type == "measurable":
            habit.current_count += 1
            habit.completed = habit.current_count >= habit.target_count
            habit.save()
            return JsonResponse({"message": "Habit progress updated", "new_progress": habit.current_count, "target": habit.target_count})

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
@login_required
def complete_habit(request, habit_id):
    try:
        habit = Habit.objects.get(id=habit_id, user=request.user)
    except Habit.DoesNotExist:
        return JsonResponse({"error": "Habit not found"}, status=404)

    if request.method == "POST":
        habit.completed = True
        habit.save()
        return JsonResponse({"message": "Habit marked as completed"})


def reset_habits():
    Habit.objects.update(current_count=0, completed=False)
    print("Daily habit reset completed.")
