def to_bool(value):
    if value in ['True', 'true']:
        return True
    elif value in ['False', 'false']:
        return False
    else:
        return None
