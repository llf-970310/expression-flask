from app.celery_manage.task import collect_history_to_analysis, move_current_to_history


class CeleryConfig:
    SCHEDULER_API_ENABLED = True
    JOBS = [
        {
            'id': 'collect_history_to_analysis',
            'func': collect_history_to_analysis,
            'args': '',
            'trigger': {
                # 5:36 分钟同步一次
                'type': 'cron',
                'day_of_week': "0-6",
                'hour': '5',
                'minute': '36'
            }
        },
        {
            'id': 'move_current_to_history',
            'func': move_current_to_history,
            'args': '',
            'trigger': {
                # 3:52 分钟同步一次
                'type': 'cron',
                'day_of_week': "0-6",
                'hour': '3',
                'minute': '52'
            }
        }
        # {
        #     'id': 'test_db',
        #     'func': test_db,
        #     'args': '',
        #     'trigger': 'interval',
        #     'seconds': 60
        # }
    ]
