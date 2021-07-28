# gitlab-webhook-flask.py
#
# A hanfler for GitLab Webhooks. Currently only handles push events
# sent upon branch deletion.
#
# Copyright 2021 Checkmarx
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from http import HTTPStatus
from flask import Flask, request, jsonify
from logging.config import dictConfig
import os

from CheckmarxPythonSDK.CxRestAPISDK import ProjectsAPI

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'WARN')
CX_PROJECT_PATTERN = os.environ.get('CX_PROJECT_PATTERN',
                                    '{project_path_with_namespace}-{branch_name}')

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': LOG_LEVEL,
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
cx = ProjectsAPI()

GITLAB_TOKEN = os.environ['GITLAB_TOKEN']

class PushEvent:

    def __init__(self, data):

        self.before = data['before']
        self.after = data['after']
        self.ref = data['ref']
        self.checkout_sha = data['checkout_sha']
        self.project_name = data['project']['name']
        self.project_namespace = data['project']['namespace']
        self.project_path_with_namespace = data['project']['path_with_namespace']

        # The branch name is the last component of the ref value
        bits = self.ref.split('/')
        self.branch_name = bits[-1]


    def format(self, pattern):

        pattern = pattern.replace('{branch_name}', self.branch_name)
        pattern = pattern.replace('{project_name}', self.project_name)
        pattern = pattern.replace('{project_namespace}', self.project_name)
        pattern = pattern.replace('{project_path_with_namespace}',
                                  self.project_path_with_namespace)
        pattern = pattern.replace('/', '-')
        return pattern

@app.route('/env', methods=['GET'])
def env():
    app.logger.debug('Calling /env')
    return jsonify(dict(os.environ)), HTTPStatus.OK


@app.route('/health', methods=['GET'])
def health():
    app.logger.debug('Calling /health')
    return jsonify({'message':'healthy'}), HTTPStatus.OK


@app.route('/webhook', methods=['POST'])
def webhook():
    app.logger.debug('Calling /webhook')
    if request.method == 'POST':
        return handle_post()
    else:
        abort(400)

def handle_post():
    app.logger.info('handle_post: starting')
    try:
        if validate_token():
            return handle_push_event()
        else:
            return warn('bad token', HTTPStatus.UNAUTHORIZED)
    finally:
            app.logger.info('handle_post: ending')


def validate_token():
    app.logger.debug('validate_token: starting')
    return request.headers.get('X-Gitlab-Token') == GITLAB_TOKEN


def handle_push_event():
    app.logger.debug('Handling push event')
    if not request.json:
        return warn('Either content-type is not application/json or body is not JSON data', HTTPStatus.BAD_REQUEST)
    try:
        push_event = PushEvent(request.json)
    except KeyError:
        return warn('Required fields missing from request body', HTTPStatus.BAD_REQUEST)

    if int(push_event.after, 16) == 0 and push_event.checkout_sha is None:
            return handle_branch_deletion(push_event)
    else:
        app.logger.debug('Not a branch deletion push event')
        return '', HTTPStatus.NO_CONTENT


def handle_branch_deletion(push_event):
    app.logger.debug('Handling branch deletion')
    cx_project_name = push_event.format(CX_PROJECT_PATTERN)
    matches = []
    projects = cx.get_all_project_details()
    try:
        for project in projects:
            if project.name == cx_project_name:
                matches.append(project)

        if len(matches) == 0:
            app.logger.warn(f'delete_cx_project: {cx_project_name} no matching project')
            return '', HTTPStatus.NO_CONTENT
        elif len(matches) > 1:
            app.logger.warn('delete_cx_project: {cx_project_name} multiple matching projects')
            return '', HTTPStatus.NO_CONTENT

        cx.delete_project_by_id(matches[0].project_id)
        app.logger.info(f'delete_cx_project: project {cx_project_name} deleted')
        return '', HTTPStatus.NO_CONTENT

    except Exception as e:
        print(f'delete_cx_project: error: {e}')


def warn(msg, status):
    app.logger.warn(msg)
    return jsonify({'message': msg}), status
