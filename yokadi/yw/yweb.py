#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Web interface for yokadi

@author: Benjamin Port (benjamin.port@brobase.fr)
@license: GPL v3 or later
"""
import json

from flask import Flask, render_template, flash, redirect, request, jsonify
from flask.ext.restful import Api, Resource, fields, marshal_with, reqparse, marshal
from sqlobject import LIKE, AND, SQLObjectNotFound
from sqlobject.sqlbuilder import LEFTJOINOn
from yokadi.core import db, dbutils
from yokadi.core.db import Project, Task, TaskKeyword
from yokadi.core.yokadiexception import YokadiException

app = Flask(__name__)
app.secret_key = 'some_secret'
api = Api(app)

def get_db():
    # db.connectDatabase("/home/ben/yokadi-test.db")
    db.connectDatabase("/home/ben/.yokadi.db")
    db.setDefaultConfig()

@app.route('/')
def show_task_list():
    projectList = list(Project.select())
    projectTaskTupleList = []
    for project in projectList:
        taskList = Task.select(AND(Task.q.projectID == project.id), distinct=True,
                               join=LEFTJOINOn(Task, TaskKeyword, Task.q.id == TaskKeyword.q.taskID))
        projectTaskTupleList.append((project, taskList))
    return render_template('task_list.html', projectList=projectTaskTupleList)

@app.route('/task/add')
@app.route('/task/edit/<int:task_id>')
def task_add(task_id=-1):
    if task_id == -1: # add task
        pass
    else: # edit task
        pass
    return render_template('task_add.html')

@app.route('/task/<int:task_id>')
def show_task_detail(task_id):
    try:
        task = dbutils.getTaskFromId(task_id)
    except YokadiException:
        return "No task with {0} id".format(task_id)
    return render_template('task_detail.html', task=task)

@app.route('/task/delete/<int:task_id>')
def task_delete(task_id):
    try:
        Task.delete(task_id)
        flash("Task {0} well deleted".format(task_id), "alert-success")
    except SQLObjectNotFound:
        flash("Can't delete task, there is no task with the following id: {0}".format(task_id), 'alert-danger')
    return redirect("/")


keyword_fields = {
    'id': fields.Integer,
    'name': fields.String,
}

project_fields = {
    'uri': fields.Url('project', absolute=True),
    'id': fields.Integer,
    'name': fields.String,
    'active': fields.Boolean,
    'keywords': fields.List(fields.Nested(keyword_fields)),
}

task_fields = {
    'uri': fields.Url('task', absolute=True),
    'id': fields.Integer,
    'title': fields.String,
    'description': fields.String,
    'creationDate': fields.DateTime,
    'dueDate': fields.DateTime,
    'doneDate': fields.DateTime,
    'status': fields.String,
    'urgency': fields.Integer,
    'keywords': fields.List(fields.Nested(keyword_fields)),
}

task_with_project_id_fields = dict.copy(task_fields)
task_with_project_id_fields['project'] = fields.Nested(project_fields)

tasks_by_project_fields = {
    'project': fields.Nested(project_fields),
    'tasks': fields.List(fields.Nested(task_fields))
}


class TaskApi(Resource):
    @marshal_with(task_fields)
    def get(self, id):
        try:
            return Task.get(id)
        except SQLObjectNotFound:
            return "Not here", 404 # TODO handle error in a better way

    def post(self, id):
        pass

    def put(self, id):
        pass

    def delete(self, id):
        try:
            Task.delete(id)
        except SQLObjectNotFound:
            return "Not here", 404 # TODO handle error in a better way

api.add_resource(TaskApi, '/api/task/<int:id>', endpoint = 'task')


class ProjectsApi(Resource):
    @marshal_with(project_fields)
    def get(self):
        return list(Project.select())

api.add_resource(ProjectsApi, '/api/projects', endpoint='projects')


class ProjectApi(Resource):
    def get(self, id):
        try:
            return marshal(project_fields, Project.get(id))
        except SQLObjectNotFound:
            return "Not here", 404 # TODO handle error in a better way

    def post(self):
        pass

    def put(self):
        pass

    def delete(self, id):
        try:
            Project.delete(id)
        except SQLObjectNotFound:
            return "Not here", 404 # TODO handle error in a better way

api.add_resource(ProjectApi, '/api/project/<int:id>', endpoint='project')


class TasksApi(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('group_by_project', type = bool, default = True, help = 'Group task by project', location = 'args')
        # TODO manaage tasks per page
    def get(self):
        if self.reqparse.parse_args()['group_by_project']:
            projectList = list(Project.select())
            tasks_by_project = []
            for project in projectList:
                taskList = Task.select(AND(Task.q.projectID == project.id), distinct=True,
                                       join=LEFTJOINOn(Task, TaskKeyword, Task.q.id == TaskKeyword.q.taskID))
                tasks_by_project.append({'project': project, 'tasks': taskList})
            return marshal(tasks_by_project, tasks_by_project_fields)

        else:
            task_list = list(Task.select())
            return marshal(task_list, task_with_project_id_fields)

api.add_resource(TasksApi, '/api/tasks', endpoint='tasks')


if __name__ == "__main__":
    get_db()
    app.run(debug=True)
