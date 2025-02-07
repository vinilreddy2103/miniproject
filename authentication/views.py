from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from authentication.models import CustomUser  # Use your CustomUser model

def signup(request):
    if request.user.is_authenticated:  # Redirect if user is already logged in
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

def login(request):
    if request.user.is_authenticated:  # Redirect if user is already logged in
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, "Login successful!")
            
            # Redirect to the original requested page or home
            next_url = request.GET.get("next")  
            return redirect(next_url if next_url else "home")

        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "login.html")

def home(request):
    if not request.user.is_authenticated:  # Redirect to login if user is not logged in
        messages.error(request, "You must be logged in to access this page.")
        return redirect("login")

    return render(request, "home.html")

def logout(request):
    auth_logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")  # Redirect to login page after logout
