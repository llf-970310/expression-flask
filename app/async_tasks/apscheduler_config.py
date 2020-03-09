from __future__ import absolute_import

from apscheduler.jobstores.mongodb import MongoDBJobStore, MongoClient
from flask_apscheduler import APScheduler as _BaseAPScheduler

from .ap_tasks_impl import collect_history_to_analysis, move_current_to_history, func_example, user_based_cf
from app_config import MongoConfig


class APScheduler(_BaseAPScheduler):
    def run_job(self, id, jobstore=None):
        with self.app.app_context():
            super().run_job(id=id, jobstore=jobstore)


client = MongoClient(host=MongoConfig.host, port=MongoConfig.port, username=MongoConfig.user,
                     password=MongoConfig.password, authSource=MongoConfig.db,
                     authMechanism=MongoConfig.auth)  # 创建数据库连接


class SchedulerConfig:
    SCHEDULER_API_ENABLED = False  # 不开启自带api
    SCHEDULER_JOBSTORES = {  # 存储位置
        'default': MongoDBJobStore(database='expression', collection='jobs', client=client)
    }
    # JOBS = [{}]  # 任务应动态检查加载避免冲突复写，不要在此直接定义


class AvailableJobs(object):
    """
    若下任务定义未加 'replace_existing': True 则以数据库为准，更新任务时需手动删库
    """
    _available_jobs = {
        'collect_history_to_analysis': {
            'job': {
                'func': collect_history_to_analysis,
                'args': '',
                'trigger': {
                    # 4:36 同步一次
                    'type': 'cron',
                    'day_of_week': "0-6",
                    'hour': 4,
                    'minute': 36
                }
            },
            'description': '收集历史测试进行分析'
        },
        'move_current_to_history': {
            'job': {
                'func': move_current_to_history,
                'args': '',
                'trigger': {
                    'type': 'cron',
                    'day_of_week': "0-6",
                    'hour': 3,
                    'minute': 20
                }
            },
            'description': '移动已完成的测试到history collection'
        },
        'user_based_cf': {
            'job': {
                'func': user_based_cf,
                'args': '',
                'trigger': {
                    # 2:50
                    'type': 'cron',
                    'day_of_week': "0-6",
                    'hour': 2,
                    'minute': 50
                }
            },
            'description': '定时计算用户相似性'
        },
        'example task': {
            'job': {
                'func': func_example,
                'args': '',
                'trigger': 'interval',
                'minutes': 10,
                # 'seconds': 10,
                'replace_existing': True
            },
            'description': '一个定时任务示例'
        }
    }

    @classmethod
    def jobs(cls):
        ret = []
        for task_id in cls._available_jobs:
            job = cls._available_jobs[task_id].get('job')
            job.update({'id': task_id})
            ret.append(job)
        return ret

    @classmethod
    def get_new_available_jobs(cls, stored_job_ids: list):
        ret = []
        for task_id in cls._available_jobs:
            job = cls._available_jobs[task_id].get('job')
            job.update({'id': task_id})
            replace = job.get('replace_existing', False)
            if (task_id not in stored_job_ids) or (replace is True):
                ret.append(job)
        return ret

    @classmethod
    def get_description(cls, task_id):
        job_wrapped = cls._available_jobs.get(task_id)
        if job_wrapped:
            return job_wrapped.get('description')
        return None
