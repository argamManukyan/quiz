from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect

from millionaire.messages import RIGHT_ANSWER
from quiz.models import Answer, Question, UserQuiz, UserQuizResult


class AnswerTabularInline(admin.TabularInline):
    extra = 1
    model = Answer


class UserQuizResultTabularInline(admin.TabularInline):
    extra = 1
    model = UserQuizResult


@admin.register(Question)
class QuestionModelAdmin(admin.ModelAdmin):
    inlines = [AnswerTabularInline]

    def change_view(self, request, object_id, form_url="", extra_context=None):
        total_forms = "".join([i for i in list(request.POST.keys()) if 'TOTAL_FORMS' in i])

        if request.POST.get(total_forms):
            s = list(
                filter(
                    lambda k: request.POST.get(f'answers-{k}-is_correct', '') == 'on',
                    range(int(request.POST.get(total_forms)))
                )
            )

            if not s:
                messages.error(request, RIGHT_ANSWER)
                last_link = request.META.get('HTTP_REFERER')
                return HttpResponseRedirect(last_link)

        return super().change_view(request, object_id, form_url="", extra_context=None)

@admin.register(UserQuiz)
class UserQuizAdmin(admin.ModelAdmin):
    inlines = [UserQuizResultTabularInline]