import json
from typing import Union

from django.contrib.auth.decorators import login_required
from django.db.models import QuerySet, Count, Sum, F, Value, CharField
from django.db.models.functions import Concat
from django.http import JsonResponse, HttpRequest
from django.shortcuts import render
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views import View

from quiz.models import Question, UserQuiz, Answer, UserQuizResult


@login_required(login_url="login")
def quiz_page(request):
    is_last = False  # Trigger for finish button

    user_passed_questions = Question.objects.filter(
        userquiz__user=request.user, userquiz__passed=True
    ).values_list('id', flat=True)  # Getting passed quiz's

    non_passed_quiz = UserQuiz.objects.filter(user=request.user, passed=False)  # Getting non passed quiz's

    non_passed_questions = Question.objects.exclude(
        id__in=user_passed_questions
    ).order_by('?').values_list('id', flat=True)[:5]  # Getting questions randomly

    quiz = ""

    if non_passed_quiz.exists():
        quiz = non_passed_quiz.first()
        questions_qty = non_passed_quiz.aggregate(
            questions_qty=Count("quiz_answers"),
        )

        is_last = bool(quiz.question.count() - questions_qty.get("questions_qty", 0) == 1)

    else:
        if non_passed_questions:
            quiz = UserQuiz.objects.create(user_id=request.user.id)
            quiz.question.add(*non_passed_questions)
            quiz.save()
        else:
            messages.add_message(
                request,
                message="You have passed all of the quiz's. Please try later. 🤔",
                extra_tags="danger",
                level=messages.ERROR
            )

    return render(request, 'quiz/quiz.html', {"quiz": quiz, "is_last": is_last})


@method_decorator(login_required(login_url='login'), name='dispatch')
class AnswerQuizView(View):

    @staticmethod
    def validate_data(*, question_id: int, answer_id: int, request: HttpRequest) -> Union[JsonResponse, tuple]:
        """Validates and gives quiz and filtered question"""

        if not question_id or not answer_id:
            return JsonResponse({"detail": "Please make sure is the given data correct ?"}, status=422)

        question: QuerySet[Question] = Question.objects.filter(id=question_id)
        answer: Answer = Answer.objects.filter(id=answer_id).first()

        if not question.first():
            return JsonResponse({"detail": "The question is not defined"}, status=400)

        if not answer:
            return JsonResponse({"detail": "The answer is not defined"}, status=400)

        correct_quiz: QuerySet[Question] = question.filter(answers__in=[answer_id])

        if not correct_quiz.exists():
            return JsonResponse({"detail": "The answer does not belong to the question"}, status=400)

        quiz: UserQuiz = UserQuiz.objects.filter(user_id=request.user.id, passed=False).order_by('-id').first()

        if not quiz:
            return JsonResponse({"detail": "You do not have any active quiz."}, status=400)

        if not quiz.question.filter(id__in=[question_id]).exists():
            return JsonResponse({"detail": "The given question does not belong to your quiz"}, status=400)

        if quiz.quiz_answers.filter(question_id=question_id).exists():
            return JsonResponse({"detail": "You already have answered this question"}, status=400)

        return quiz, correct_quiz

    @staticmethod
    def combine_response(
            *,
            question_id_list: list,
            is_right: bool,
            question_id: int,
            answer_id: int,
            quiz: UserQuiz,
            request: HttpRequest
    ) -> dict:
        if question_id_list:
            data = {
                "quiz_pass": False,
                "is_right": is_right,
                "right_answer": Answer.objects.filter(question_id=question_id, is_correct=True).first().id,
                "given_answer": answer_id,
                "result": render_to_string(
                    'includes/question_block.html', {
                        "question": quiz.question.filter(id=question_id_list[0]).first(),
                        "is_last": bool(question_id_list)
                    },
                    request
                )
            }
        else:
            messages.success(request, f"You have passed this quiz, and have got {quiz.score} points. 😉")
            data = {
                "quiz_pass": True,
                "result": render_to_string(
                    'includes/question_block.html', {
                        "quiz_pass": True
                    },
                    request
                )
            }
            quiz.passed = True
            quiz.save()

        return data

    def post(self, request: HttpRequest, *args, **kwargs):

        if not request.user.is_authenticated:
            return JsonResponse({"detail": "Please sign in for perform this action"}, status=401)
        data = json.loads(request.body)
        question_id = data.pop('question', '')
        answer_id = data.pop('answer', '')

        validated_data = self.validate_data(question_id=question_id, answer_id=answer_id, request=request)
        if isinstance(validated_data, JsonResponse):
            return validated_data
        quiz, correct_quiz = validated_data
        is_right = correct_quiz.filter(answers__is_correct=True, answers__in=[answer_id]).exists()

        # gathering quiz result for the particular user
        quest_result = {
            "quiz_id": quiz.id,
            "answer_id": answer_id,
            "is_correct": is_right,
            "question_id": question_id
        }

        UserQuizResult.objects.create(**quest_result)

        # filtering and getting rest of the question id list
        question_id_list = [i for i in quiz.question.values_list('id', flat=True)]

        if is_right:
            quiz.score += correct_quiz.first().point

        quiz.save()

        # filtering and getting out the rest of the questions of which have not been answered
        question_id_list = list(
            filter(lambda x: x not in list(
                quiz.quiz_answers.values_list('question_id', flat=True)
            ), question_id_list)
        )

        # combine response
        response = self.combine_response(
            question_id=question_id,
            answer_id=answer_id,
            is_right=is_right,
            question_id_list=question_id_list,
            quiz=quiz,
            request=request
        )

        return JsonResponse(response)


@method_decorator(login_required(login_url="login"), name='dispatch')
class TopPlayersView(View):
    """Returns top 10 players with their total scores"""

    def get(self, request, *args, **kwargs):
        sorted_players = UserQuiz.objects.annotate(
            full_name=Concat(
                F('user__first_name'),
                Value(' '), F('user__last_name'),
                Value(' By ID:'), F('user_id'),
                output_field=CharField())
        ).values('full_name').annotate(
            score_sum=Sum('score')
        ).order_by('-score_sum')[:10]

        return render(request, 'quiz/winners_list.html', {"sorted_players": sorted_players})
