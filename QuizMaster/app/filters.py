def to_set(value):
    return set(value.split(','))

def register_filters(app):
    app.jinja_env.filters['to_set'] = to_set