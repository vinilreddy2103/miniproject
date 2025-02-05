from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout as auth_logout
from django.contrib import messages

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not username or not email or not password:
            messages.error(request, "All fields are required.")
            return render(request, "signup.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, "signup.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, "signup.html")

        # Create the user
        user = User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created successfully. Please log in.")
        return redirect("login")

    return render(request, "signup.html")

def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, "Login successful!")
            return redirect("home")  # Redirect to home page after login
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "login.html")

@login_required  # Ensures only logged-in users can access this page
def home(request):
    return render(request, "home.html")

def logout(request):
    auth_logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")  # Redirect to login page after logout
