from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from habit.models import Habit
from django.utils.timezone import now
import json
from datetime import date

def reset_user_habits(user):
    today = now().date()
    habits = Habit.objects.filter(user=user)

    habits_reset = 0  # Track how many habits are reset

    for habit in habits:
        if habit.last_reset_date == today:
            continue  # Skip if already reset today

        if habit.habit_type == "measurable":
            habit.current_count = 0  # Reset progress for measurable habits
            habit.completed = False
        else:
            habit.completed = False  # Mark non-measurable habits as incomplete

        habit.last_reset_date = today  # Update last reset date
        habit.save()
        habits_reset += 1  # Increment counter

    return habits_reset

from datetime import date
from .models import Habit

def check_streak(user):
    """Resets streak to zero if a day is missed."""
    today = date.today()
    habits = Habit.objects.filter(user=user)

    for habit in habits:
        if habit.last_completed:
            days_since_last = (today - habit.last_completed).days
            if days_since_last > 1:
                habit.streak = 0  # Reset streak if a day is missed
                habit.last_completed = None  # Set last completed to null
                habit.save()

@login_required
def home(request):
    reset_user_habits(request.user)  # Reset habits when the user logs in
    check_streak(request.user)
    return render(request, "habit/home.html")


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
            "streak": habit.streak,
            "completed_dates": habit.completed_dates,
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
                completed=False,
                last_reset_date=now().date()
            )
            return JsonResponse({"message": "Habit added successfully!", "id": habit.id}, status=201)

        except (json.JSONDecodeError, ValueError) as e:
            print("Error in add_habit:", str(e))  # Debugging line
            return JsonResponse({"error": "Invalid JSON data"}, status=400)


@csrf_exempt
@login_required
def update_habit(request, habit_id):
    try:
        habit = Habit.objects.get(id=habit_id, user=request.user)

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
                return JsonResponse(
                    {"message": "Habit incremented", "new_progress": habit.current_count, "target": habit.target_count},
                    status=200,
                )

            elif "completed" in data:
                habit.completed = data["completed"]
                habit.save()
                return JsonResponse({"message": "Habit completion status updated"}, status=200)

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
            return JsonResponse(
                {"message": "Habit progress updated", "new_progress": habit.current_count, "target": habit.target_count}
            )

    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
@login_required
def complete_habit(request, habit_id):
    try:
        habit = Habit.objects.get(id=habit_id, user=request.user)
    except Habit.DoesNotExist:
        return JsonResponse({"error": "Habit not found"}, status=404)

    if request.method == "POST":
        today = date.today().isoformat()

        if today not in habit.completed_dates:
            habit.completed_dates.append(today)  # Store today's date
            habit.update_streak()  # Update streak
            habit.save()

        return JsonResponse({
            "message": "Habit marked as completed",
            "streak": habit.streak,
            "last_completed": habit.last_completed.strftime("%Y-%m-%d"),
            "completed_dates": habit.completed_dates,
        })


@login_required
def habit_detail(request, habit_id):
    try:
        habit = Habit.objects.get(id=habit_id, user=request.user)
        return JsonResponse({
            "id": habit.id,
            "name": habit.name,
            "habit_type": habit.habit_type,
            "current_count": habit.current_count,
            "target_count": habit.target_count,
            "completed": habit.completed,
            "streak": habit.streak,
            "completed_dates": habit.completed_dates,
        })
    except Habit.DoesNotExist:
        return JsonResponse({"error": "Habit not found"}, status=404)
