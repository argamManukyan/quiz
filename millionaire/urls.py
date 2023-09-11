from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt
from quiz.views import quiz_page, AnswerQuizView, TopPlayersView
from users.views import register, login_user, logout_user

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', quiz_page, name="quiz_page"),
    path('answer/', csrf_exempt(AnswerQuizView.as_view()), name="answer_quiz"),
    path('top-players/', TopPlayersView.as_view(), name="top_players"),
    path('register/', csrf_exempt(register), name="register"),
    path('login/', csrf_exempt(login_user), name="login"),
    path('logout/', logout_user, name="logout"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)