from functools import partial

from millionaire.utils import handle_fail_response
from millionaire import messages

InvalidDataResponse = partial(handle_fail_response, message=messages.INVALID_DATA, status_code=422)()
QuestionUndefinedResponse = partial(handle_fail_response, message=messages.QUESTION_UNDEFINED)()
AnswerUndefinedResponse = partial(handle_fail_response, message=messages.ANSWER_UNDEFINED)()
AnswerDoesNotBelongToQuestionResponse = partial(handle_fail_response, message=messages.ANSWER_NOT_BELONG_TO_QUESTION)()
QuestionDoesNotBelongToQuizResponse = partial(handle_fail_response, message=messages.QUESTION_NOT_BELONG_TO_QUIZ)()
NotActiveQuizResponse = partial(handle_fail_response, message=messages.NOT_ACTIVE_QUIZ)()
AlreadyAnsweredResponse = partial(handle_fail_response, message=messages.ALREADY_ANSWERED)()
UnAuthorizedResponse = partial(handle_fail_response, message=messages.UNAUTHORIZED, status_code=401)()