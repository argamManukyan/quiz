from django.template import Library
from django.db.models import Q
register = Library()


@register.filter("question")
def question_filter(userquiz):
    if isinstance(userquiz, str):
        return []
    passed_questions = userquiz.quiz_answers.values_list('question_id', flat=True)
    answered_questions = userquiz.question.filter(~Q(id__in=passed_questions))
    if answered_questions:
        return answered_questions.first()
    return []