#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 20-3-07

from apscheduler.jobstores.base import ConflictingIdError
from flask import current_app
from app.auth.util import admin_login_required

from . import ap_view

from flask_apscheduler import api
from flask_apscheduler.json import jsonify, dumps, loads
from .apscheduler_config import AvailableJobs


# 所有通过api进行的调用只在flask app运行起来之后才可用

def add_job_from_dict(data):
    try:
        job = current_app.apscheduler.add_job(**data)
        return jsonify(job)
    except ConflictingIdError:
        return jsonify(dict(error_message='Job %s already exists.' % data.get('id')), status=409)
    except Exception as e:
        return jsonify(dict(error_message=str(e)), status=500)


# flask_apscheduler.api:
#   get_scheduler_info, get_jobs, get_job, add_job, delete_job, update_job, pause_job, resume_job, run_job


@ap_view.route('/jobs', methods=['GET'])
@admin_login_required
def get_jobs():
    """Gets all scheduled jobs."""
    job_states = []
    jobs = current_app.apscheduler.get_jobs()
    for job in jobs:
        desc = AvailableJobs.get_description(job.id)
        temp = loads(dumps(job))
        temp.update({'desc': desc})
        job_states.append(temp)
    return jsonify(job_states)


@ap_view.route('/jobs/<job_id>', methods=['GET'])
@admin_login_required
def get_job(job_id):
    # some wrapper codes
    return api.get_job(job_id)


@ap_view.route('/jobs/<job_id>/pause', methods=['POST'])
@admin_login_required
def pause_job(job_id):
    return api.pause_job(job_id)


@ap_view.route('/jobs/<job_id>/resume', methods=['POST'])
@admin_login_required
def resume_job(job_id):
    return api.resume_job(job_id)

# in flask_apscheduler.scheduler._load_api:
#     """
#     Add the routes for the scheduler API.
#     """
#     self._add_url_route('get_scheduler_info', '', api.get_scheduler_info, 'GET')
#     self._add_url_route('add_job', '/jobs', api.add_job, 'POST')
#     self._add_url_route('get_job', '/jobs/<job_id>', api.get_job, 'GET')
#     self._add_url_route('get_jobs', '/jobs', api.get_jobs, 'GET')
#     self._add_url_route('delete_job', '/jobs/<job_id>', api.delete_job, 'DELETE')
#     self._add_url_route('update_job', '/jobs/<job_id>', api.update_job, 'PATCH')
#     self._add_url_route('pause_job', '/jobs/<job_id>/pause', api.pause_job, 'POST')
#     self._add_url_route('resume_job', '/jobs/<job_id>/resume', api.resume_job, 'POST')
#     self._add_url_route('run_job', '/jobs/<job_id>/run', api.run_job, 'POST')

# Just keep these urls, and make some wrappers
