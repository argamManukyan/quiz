from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from millionaire.utils import check_is_user_logged
from millionaire import messages as custom_messages
from users.services import login_page_service, register_page_service


@check_is_user_logged
def register(request):
    """Creating new user accounts"""

    if request.method == 'POST':
        try:

            # Create user
            obj = register_page_service.create_user(request)

            if not obj:
                return redirect("register")

            register_page_service.messaging_success(
                message=custom_messages.USER_CREATED.format(obj.username),
                request=request
            )

            return redirect("login")
        except Exception as e:
            register_page_service.messaging_fail(message=f"{e.args}", request=request)

    return render(request, "users/register.html")


@check_is_user_logged
def login_user(request):
    """Login user"""
    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = login_page_service.find_user(username)

        if not user:
            login_page_service.messaging_fail(message=custom_messages.USER_DOES_NOT_EXISTS, request=request)
            return redirect("login")

        # Checking is the user password true
        if not user.check_password(password):
            login_page_service.messaging_fail(message=custom_messages.INVALID_CREDENTIALS, request=request)
            return redirect("login")

        user = authenticate(username=username, password=password)
        if not user:
            login_page_service.messaging_fail(message=custom_messages.INVALID_CREDENTIALS, request=request)
            return redirect("login")

        login(request, user)
        login_page_service.messaging_success(message=custom_messages.LOGGED, request=request)
        return redirect("quiz_page")

    return render(request, "users/login.html")


@login_required(login_url="login")
def logout_user(request):
    """logout function"""
    logout(request)
    return redirect("login")
