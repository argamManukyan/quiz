import functools
from typing import Callable, Union

from django.db import models
from django.http import JsonResponse
from django.shortcuts import redirect

from millionaire import constants


class BaseModel(models.Model):
    """Abstract model for tracking created and updated date of each object"""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def check_is_user_logged(func: Callable):
    """Checks is the request user logged in, if yes returns user to `quiz_page`"""
    @functools.partial
    def wrapper(request):
        if request.user.is_authenticated:
            return redirect("quiz_page")
        return func(request)
    return wrapper


def handle_fail_response(message: str, status_code=400) -> JsonResponse:
    """Error message handler"""

    return JsonResponse({constants.ERROR_MESSAGE_KEY: message}, status=status_code)


def handle_success_response(message: Union[str, dict], status_code=200):
    """Success response handler"""
    return JsonResponse({constants.SUCCESS_MESSAGE_KEY: message}, status=status_code)