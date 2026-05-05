def get_model_id(obj, candidates):
    for name in candidates:
        if hasattr(obj, name):
            return getattr(obj, name)
    return None


def get_model_name(obj, candidates, fallback):
    for name in candidates:
        if hasattr(obj, name):
            return str(getattr(obj, name))
    return fallback


def get_answer_text(answer):
    for name in ("answer_text", "text", "title", "name_answer", "value"):
        if hasattr(answer, name):
            value = getattr(answer, name)
            if value is not None:
                return str(value)
    if isinstance(answer, str):
        return answer
    return None