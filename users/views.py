import time

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required

from millionaire.utils import check_is_user_logged

User = get_user_model()


@check_is_user_logged
def register(request):
    """Creating new user accounts"""
    if request.method == 'POST':
        try:

            # Getting requested data
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            password = request.POST.get("password", "")
            username = f"{first_name}_{int(time.time())}"  # My version of username generation

            # Just password validation example (Not included regexp checking for symbols and uppercase's and digits )
            if len(password) < 3:
                messages.add_message(
                    request,
                    level=messages.ERROR,
                    message=f"Password should contains at least 3 symbols",
                    extra_tags="danger"
                )
                return redirect("register")

            # User creation
            User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            messages.success(request, f"User created successfully, your username is {username}")

            return redirect("login")
        except Exception as e:
            messages.add_message(
                request,
                level=messages.ERROR,
                message=f"{e.args}",
                extra_tags="danger"
            )

    return render(request, "users/register.html")


@check_is_user_logged
def login_user(request):
    """Login user"""
    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = User.objects.filter(username=username).first()  # Getting the first matching object

        if not user:
            messages.add_message(
                request,
                level=messages.ERROR,
                message="User with given username does not exists",
                extra_tags="danger"
            )

            return redirect("login")

        # Checking is the user password true
        if not user.check_password(password):

            messages.add_message(
                request,
                level=messages.ERROR,
                message="The credentials are incorrect, please try again.",
                extra_tags="danger"
            )

            return redirect("login")

        user = authenticate(username=username, password=password)
        if not user:
            messages.add_message(
                request,
                level=messages.ERROR,
                message="The credentials are incorrect, please try again.",
                extra_tags="danger"
            )

            return redirect("login")

        login(request, user)
        messages.success(request, "You are logged in successfully")
        return redirect("quiz_page")

    return render(request, "users/login.html")


@login_required(login_url="login")
def logout_user(request):
    """logout function"""
    logout(request)
    return redirect("login")
