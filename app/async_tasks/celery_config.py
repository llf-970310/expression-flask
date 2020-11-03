from kombu import Queue, Exchange

"""
配置队列，若和命令行冲突，这些配置会覆盖命令行配置
"""

CELERY_QUEUES = (
    # Queue('for_q_type3', Exchange('for_q_type3'), routing_key='for_q_type3', consumer_arguments={'x-priority': 10}),
    Queue('q_type3', Exchange('q_type3'), routing_key='q_type3', queue_arguments={'x-max-priority': 100}),
    Queue('q_type12', Exchange('q_type12'), routing_key='q_type12', queue_arguments={'x-max-priority': 2}),
    Queue('q_pre_test', Exchange('q_pre_test'), routing_key='q_pre_test', queue_arguments={'x-max-priority': 500}),
    Queue('default', Exchange('default'), routing_key='default', queue_arguments={'x-max-priority': 1}),
)  # consumer_arguments={'x-priority': 5}   数字越大，优先级越高

BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 86400}

CELERY_DEFAULT_QUEUE = 'default'
CELERY_DEFAULT_EXCHANGE = 'default'
CELERY_DEFAULT_ROUTING_KEY = 'default'
CELERY_ROUTES = {
    # -- HIGH PRIORITY QUEUE -- #
    'analysis_3': {'queue': 'q_type3'},
    'analysis_pretest': {'queue': 'q_pre_test'},
    # -- LOW PRIORITY QUEUE -- #
    'analysis_12': {'queue': 'q_type12'},
}

CELERYD_MAX_TASKS_PER_CHILD = 500  # 及时释放内存
CELERYD_PREFETCH_MULTIPLIER = 2
