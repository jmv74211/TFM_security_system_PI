from celery import Celery

def make_celery(app):
    celery = Celery(
        app.import_name,
        #result_backend=app.config['CELERY_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    #celery.conf.update(app.config)
    celery.conf.update(task_track_started=True,
                    result_backend= app.config['CELERY_BACKEND'])


    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery