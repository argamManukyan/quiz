from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from millionaire.utils import BaseModel

User = get_user_model()


class Question(BaseModel):
    """Questions table"""

    question = models.CharField(max_length=255, db_index=True)
    point = models.SmallIntegerField(validators=[
        MinValueValidator(limit_value=5),
        MaxValueValidator(limit_value=20)
    ])

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"


class Answer(BaseModel):
    """Answers table"""

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    answer = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.answer

    class Meta:
        verbose_name = "Answer"
        verbose_name_plural = "Answers"

        unique_together = (
            ("question_id", "answer"),
            ("question_id", "answer", "is_correct")
        )


class UserQuiz(BaseModel):
    """User passed quiz's table"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ManyToManyField('quiz.Question')
    score = models.SmallIntegerField(default=0)
    passed = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}: {self.score}'

    class Meta:
        verbose_name = 'User quiz'
        verbose_name_plural = 'User quiz\'s'


class UserQuizResult(BaseModel):
    """Table to save user quiz results"""

    quiz = models.ForeignKey(UserQuiz, on_delete=models.CASCADE, related_name='quiz_answers')
    question_id = models.SmallIntegerField()
    answer_id = models.SmallIntegerField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.id}'
