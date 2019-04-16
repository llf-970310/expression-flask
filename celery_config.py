from app.celery_manage.task import collect_current_to_analysis, test_db


class CeleryConfig():
    SCHEDULER_API_ENABLED = True
    JOBS = [
        {
            'id': 'collect_current_to_analysis',
            'func': collect_current_to_analysis,
            'args': '',
            'trigger': {
                # 每小时的第 30 分钟同步一次
                'type': 'cron',
                'day_of_week': "0-6",
                'hour': '*',
                'minute': '30'
            }
        },
        # {
        #     'id': 'test_db',
        #     'func': test_db,
        #     'args': '',
        #     'trigger': 'interval',
        #     'seconds': 60
        # }
    ]
