from django.contrib import admin
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


@admin.register(UserQuiz)
class UserQuizAdmin(admin.ModelAdmin):
    inlines = [UserQuizResultTabularInline]