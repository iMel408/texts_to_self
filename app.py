import texts_to_self

app = texts_to_self.create_app()
celery = app.celery