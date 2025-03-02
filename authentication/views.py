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
        return redirect("habit/home")

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

def logout(request):
    auth_logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")

def landing(request):
    return redirect("auth/login")
