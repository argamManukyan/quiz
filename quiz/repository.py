from typing import Iterable

from django.db.models import QuerySet, F, Value, CharField, Sum
from django.db.models.functions import Concat

from quiz.models import Question, Answer, UserQuiz, UserQuizResult


class QuestionRepository:
    model = Question

    @classmethod
    def filter_question(cls, params: dict = None, exclude_params: dict = None) -> QuerySet[Question]:
        if not params:
            params = {}
        if not exclude_params:
            exclude_params = {}

        return cls.model.objects.filter(**params).exclude(**exclude_params)

    @classmethod
    def filter_question_based_on_qs(cls, question_qs: QuerySet[Question], params: dict):
        return question_qs.filter(**params)


class UserQuizRepository:
    model = UserQuiz

    @classmethod
    def filter_user_quiz(cls, params: dict = None) -> QuerySet[UserQuiz]:
        """Returns filtered objects regarding given params"""

        if not params:
            params = {}
        return cls.model.objects.filter(**params)

    @classmethod
    def create_user_quiz(cls, params: dict, m2m_params: Iterable = None) -> UserQuiz:
        """Returns new created object"""

        obj = cls.model.objects.create(**params)

        if m2m_params:
            obj.question.set(m2m_params)
            obj.save()

        return obj

    @classmethod
    def update_user_quiz(cls, quiz: UserQuiz, params: dict) -> UserQuiz:
        for key, value in params.items():
            setattr(quiz, key, value)
            quiz.save()
        return quiz

    @classmethod
    def update_quiz_score(cls, quiz: UserQuiz, score: int) -> None:
        quiz.score += score
        quiz.save()

    @classmethod
    def annotate_players(cls):
        return cls.model.objects.annotate(
            full_name=Concat(
                F('user__first_name'),
                Value(' '), F('user__last_name'),
                Value(' By ID:'), F('user_id'),
                output_field=CharField()
            )
        ).values('full_name').annotate(
            score_sum=Sum('score')
        )


class AnswerRepository:
    model = Answer

    @classmethod
    def get_answers(cls, filter_params: dict) -> QuerySet[Answer]:
        if not filter_params:
            filter_params = {}
        return cls.model.objects.filter(**filter_params)


class UserQuizResultRepository:
    model = UserQuizResult

    @classmethod
    def create_user_quiz_result(cls, params: dict) -> UserQuizResult:
        return cls.model.objects.create(**params)

    @classmethod
    def filter_results_of_the_quiz(cls, quiz_id: int) -> QuerySet[UserQuizResult]:
        return cls.model.objects.filter(quiz_id=quiz_id)


question_repo = QuestionRepository
user_quiz_repo = UserQuizRepository
user_quiz_result_repo = UserQuizResultRepository
answer_repo = AnswerRepository
