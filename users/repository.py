from django.contrib.auth import get_user_model
from django.db.models import QuerySet

User = get_user_model()


class UserRepository:
    model = User

    @classmethod
    def get_users(cls, filter_params: dict = None) -> QuerySet[User]:
        if not filter_params:
            filter_params = {}

        return cls.model.objects.filter(**filter_params)

    @classmethod
    def create_user(cls, payload: dict) -> User:
        return cls.model.objects.create_user(**payload)


user_repository = UserRepository
