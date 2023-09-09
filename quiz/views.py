import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest
from django.shortcuts import render
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import View

from quiz import exceptions
from millionaire import constants, messages as custom_messages
from quiz.services import QuizPageService as quiz_page_service, TopPlayersPageService
from quiz.services import AnswerQuizAPIService as answer_quiz_api_service


@login_required(login_url="login")
def quiz_page(request):
    is_last = False  # Trigger for finish button
    quiz = None

    # Getting non passed quiz's
    not_passed_quiz = quiz_page_service.get_not_passed_quiz(request=request)

    # Getting not answered questions randomly
    not_passed_questions = quiz_page_service.get_list_of_not_answered_questions(request=request)

    # In case when the player has answered all the questions
    if not not_passed_quiz.exists() and not not_passed_questions.count():
        messages.add_message(
            request,
            message=custom_messages.NOT_PASSED_QUESTIONS_MISSING,
            extra_tags=constants.DANGER_TAG,
            level=messages.ERROR
        )

    # In case when the player has not passed quiz
    elif not_passed_quiz.exists():
        quiz = not_passed_quiz.first()
        is_last = quiz_page_service.check_is_it_last_question(quiz_qs=not_passed_quiz)

    # Creating a new quiz using not answered questions
    if not_passed_questions.exists() and not not_passed_quiz.exists():
        quiz = quiz_page_service.create_user_quiz_object(request=request, questions_ids=not_passed_questions)

    return render(request, 'quiz/quiz.html', {"quiz": quiz, "is_last": is_last})


@method_decorator(login_required(login_url='login'), name='dispatch')
class AnswerQuizView(View):

    # @staticmethod
    #

    def post(self, request: HttpRequest, *args, **kwargs):

        if not request.user.is_authenticated:
            return exceptions.UnAuthorizedResponse()

        data = json.loads(request.body)
        question_id = data.pop('question', '')
        answer_id = data.pop('answer', '')

        validated_data = answer_quiz_api_service.validate_data(
            question_id=question_id,
            answer_id=answer_id,
            request=request
        )

        if isinstance(validated_data, JsonResponse):
            return validated_data

        quiz, correct_question = validated_data
        is_right = answer_quiz_api_service.filter_questions_by_qs(
            question_qs=correct_question,
            answer_id=answer_id
        ).exists()

        # gathering quiz result for the particular user and creating in once
        quest_payload = {
            "quiz_id": quiz.id,
            "answer_id": answer_id,
            "is_correct": is_right,
            "question_id": question_id
        }
        answer_quiz_api_service.create_user_quiz(quest_payload)

        # filtering and getting rest of the question id list
        question_id_list = answer_quiz_api_service.get_question_id_list(quiz_id=quiz.id)
        # question_id_list = list(quiz.question.values_list('id', flat=True))

        if is_right:
            answer_quiz_api_service.update_quiz_score(quiz, correct_question.first().point)
            # quiz.score += correct_question.first().point

        # filtering and getting out the rest of the questions of which have not been answered
        question_id_list = answer_quiz_api_service.filter_question_ids(
            question_id_list=question_id_list,
            quiz_id=quiz.id
        )
        print(
            question_id_list
        )
        # combine response
        return answer_quiz_api_service.combine_response(
            question_id=question_id,
            answer_id=answer_id,
            is_right=is_right,
            question_id_list=question_id_list,
            quiz=quiz,
            request=request
        )


@method_decorator(login_required(login_url="login"), name='dispatch')
class TopPlayersView(View):
    """Returns top 10 players with their total scores"""

    def get(self, request, *args, **kwargs):
        sorted_players = TopPlayersPageService.sort_players()
        return render(request, 'quiz/winners_list.html', {"sorted_players": sorted_players})
