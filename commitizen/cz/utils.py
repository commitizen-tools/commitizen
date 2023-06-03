from commitizen.cz import exceptions


def required_validator(answer, msg=None):
    if not answer:
        raise exceptions.AnswerRequiredError(msg)
    return answer


def multiple_line_breaker(answer, sep="|"):
    return "\n".join(line.strip() for line in answer.split(sep) if line)
