import time
from typing import Union

from django.http import HttpRequest
from django.contrib.auth import get_user_model

from millionaire import messages as custom_messages
from millionaire.utils import MessagingActions
from users.repository import user_repository

User = get_user_model()


class LoginPageService(MessagingActions):

    @classmethod
    def find_user(cls, username):
        """Returns the first matching user object"""
        return user_repository.get_users({"username": username}).first()


class RegisterPageService(MessagingActions):

    @classmethod
    def validate_password(cls, password: str, request: HttpRequest) -> bool:
        """Password validation """
        if len(password) < 3:
            super().messaging_fail(message=custom_messages.PASSWORD_VALIDATION, request=request)
            return False
        return True

    @classmethod
    def create_user(cls, request) -> Union[bool, User]:
        first_name = request.POST.get("first_name")
        password = request.POST.get("password", "")

        data = dict(
            first_name= first_name,
            last_name=request.POST.get("last_name"),
            password=password,
            username=f"{first_name}_{int(time.time())}",
        )

        # Just password validation example (Not included regexp checking for symbols and uppercase's and digits )
        if not cls.validate_password(password=password, request=request):
            return False

        # User creation
        return user_repository.create_user(data)


login_page_service = LoginPageService
register_page_service = RegisterPageService
