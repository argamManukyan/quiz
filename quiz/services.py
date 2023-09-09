from typing import Iterable, Union

from django.db.models import QuerySet, Count
from django.http import HttpRequest, JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages

from millionaire.utils import handle_success_response
from quiz import exceptions
from millionaire import messages as custom_messages
from millionaire.constants import MAX_QUESTIONS_NUM, TOP_PLAYERS_LIMIT
from quiz.models import Question, UserQuiz, UserQuizResult
from quiz.repository import question_repo, user_quiz_repo, answer_repo, user_quiz_result_repo


class QuizPageService:

    @classmethod
    def get_answered_questions(cls, *, request: HttpRequest) -> QuerySet[Question]:
        """Returns id list of answered questions"""

        params = dict(userquiz__user=request.user, userquiz__passed=True)
        return question_repo.filter_question(params=params).values_list('id', flat=True)

    @classmethod
    def get_list_of_not_answered_questions(cls, *, request: HttpRequest) -> QuerySet[Question]:
        """Returns randomly sorted id list of not answered questions"""

        exclude_params = dict(id__in=cls.get_answered_questions(request=request))

        return question_repo.filter_question(
            exclude_params=exclude_params
        ).order_by('?').values_list('id', flat=True)[:MAX_QUESTIONS_NUM]

    @classmethod
    def get_not_passed_quiz(cls, *, request: HttpRequest) -> QuerySet[UserQuiz]:
        """Returns not passed quiz"""

        params = dict(user=request.user, passed=False)
        return user_quiz_repo.filter_user_quiz(params=params)

    @classmethod
    def aggregate_and_get_answered_qty(cls, quiz_qs: QuerySet[UserQuiz], /) -> int:
        """Returns number of answered questions to the particular quiz"""
        return quiz_qs.aggregate(quiz_answers=Count("quiz_answers")).get('quiz_answers', 0)

    @classmethod
    def check_is_it_last_question(cls, *, quiz_qs: QuerySet[UserQuiz]) -> bool:
        """Returns is the question latest of the quiz question list"""
        return quiz_qs.first().question.count() - cls.aggregate_and_get_answered_qty(quiz_qs) == 1

    @classmethod
    def create_user_quiz_object(cls, *, request: HttpRequest, questions_ids: Iterable):
        """Returns user_quiz object using not passed questions"""
        params = dict(user_id=request.user.id)
        return user_quiz_repo.create_user_quiz(params=params, m2m_params=questions_ids)


class AnswerQuizAPIService:

    @classmethod
    def validate_data(cls, *, question_id: int, answer_id: int, request: HttpRequest) -> Union[JsonResponse, tuple]:
        """Validates and gives quiz and filtered question"""

        if not question_id or not answer_id:
            return exceptions.InvalidDataResponse

        question = question_repo.filter_question(dict(id=question_id))

        answer = answer_repo.get_answers(filter_params=dict(id=answer_id)).first()

        if not question.first():
            return exceptions.QuestionUndefinedResponse

        if not answer:
            return exceptions.AnswerUndefinedResponse

        correct_question = question_repo.filter_question(params=dict(id=question_id, answers__in=[answer_id]))

        if not correct_question.exists():
            return exceptions.AnswerDoesNotBelongToQuestionResponse

        quiz: UserQuiz = user_quiz_repo.filter_user_quiz(
            params=dict(user_id=request.user.id, passed=False)
        ).order_by('-id').first()

        if not quiz:
            return exceptions.NotActiveQuizResponse

        if not user_quiz_repo.filter_user_quiz(params=dict(question__in=[question_id], id=quiz.id)).exists():
            return exceptions.QuestionDoesNotBelongToQuizResponse
            # if not quiz.question.filter(id__in=[question_id]).exists():

        if user_quiz_repo.filter_user_quiz(params=dict(quiz_answers__question_id=question_id, id=quiz.id)):
            # if quiz.quiz_answers.filter().exists():
            return exceptions.AlreadyAnsweredResponse

        return quiz, correct_question

    @classmethod
    def filter_questions_by_qs(cls, question_qs: QuerySet[Question], answer_id: int) -> QuerySet[Question]:
        """Returns filtered quesryset based on the given one"""
        return question_repo.filter_question_based_on_qs(
            question_qs=question_qs,
            params=dict(answers__in=[answer_id], answers__is_correct=True)
        )

    @classmethod
    def create_user_quiz(cls, params: dict) -> UserQuizResult:
        """Returns new created UserQuiz object"""
        return user_quiz_result_repo.create_user_quiz_result(params=params)

    @classmethod
    def get_question_id_list(cls, quiz_id: int) -> Iterable[int]:
        """Returns id list of question for particular user"""
        return question_repo.filter_question({"userquiz__in": [quiz_id]}).values_list('id', flat=True)

    @classmethod
    def update_quiz_obj(cls, quiz: UserQuiz, params: dict) -> UserQuiz:
        """Updates quiz object"""
        return user_quiz_repo.update_user_quiz(quiz=quiz, params=params)

    @classmethod
    def update_quiz_score(cls, quiz: UserQuiz, score: int) -> None:
        """Increments quiz score"""
        user_quiz_repo.update_quiz_score(quiz=quiz, score=score)

    @classmethod
    def filter_question_ids(cls, question_id_list, quiz_id) -> list:
        """Returns rest of question ids that have not been answered yet"""
        return list(
            filter(
                lambda x: x not in list(
                    user_quiz_result_repo.filter_results_of_the_quiz(
                        quiz_id=quiz_id).values_list('question_id', flat=True)
                ),
                question_id_list
            )
        )

    @classmethod
    def combine_response(
        cls,
        *,
        question_id_list: list,
        is_right: bool,
        question_id: int,
        answer_id: int,
        quiz: UserQuiz,
        request: HttpRequest
    ) -> dict:
        """Combine a response for Answer API"""

        if question_id_list:
            data = {
                "quiz_pass": False,
                "is_right": is_right,
                "right_answer": answer_repo.get_answers(dict(question_id=question_id, is_correct=True)).first().id,
                "given_answer": answer_id,
                "result": render_to_string(
                    'includes/question_block.html', {
                        "question": question_repo.filter_question(dict(id=question_id_list.pop(0))).first(),
                        "is_last": not question_id_list
                    },
                    request
                )
            }
        else:
            messages.success(request, custom_messages.RESULT_MESSAGE.format(quiz_score=quiz.score))
            data = {
                "quiz_pass": True,
                "result": render_to_string(
                    'includes/question_block.html', {
                        "quiz_pass": True
                    },
                    request
                )
            }
            user_quiz_repo.update_user_quiz(quiz=quiz, params=dict(passed=True))

        return handle_success_response(data)


class TopPlayersPageService:
    @classmethod
    def sort_players(cls):
        """Sorts and returns top 10 players by score"""
        return user_quiz_repo.annotate_players().order_by('-score_sum')[:TOP_PLAYERS_LIMIT]