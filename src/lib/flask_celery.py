from celery import Celery
from kombu import Queue

def make_celery(app):
    celery = Celery(
        app.import_name,
        #result_backend=app.config['CELERY_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    #celery.conf.update(app.config)
    celery.conf.update(task_track_started=True,
                    result_backend= app.config['CELERY_BACKEND'])

    celery.conf.task_queues = (
        Queue('default',routing_key='default'),
        Queue('api_agent', routing_key='api_agent'),
        Queue('motion_agent', routing_key='motion_agent')
    )


    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.    run(*args, **kwargs)

    celery.Task = ContextTask
    return celery