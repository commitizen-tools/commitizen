from commitizen.cz import exceptions


def required_validator(ans, msg=None):
    if not ans:
        raise exceptions.AnswerRequiredError(msg)
    return ans


def multiple_line_breaker(ans, sep="|"):
    return "\n".join(line.strip() for line in ans.split(sep) if line)
