import functools
from typing import Callable

from django.db import models
from django.shortcuts import redirect


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
