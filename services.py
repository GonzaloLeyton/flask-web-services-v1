#!flask/bin/python
# -*- coding: utf-8 -*-


from flask import Flask, jsonify, request, make_response
from flask.ext.mongoengine import MongoEngine
from flask.ext.httpauth import HTTPBasicAuth
from mongoengine import *
import pymongo, os, json

auth = HTTPBasicAuth()


# Here we can check a user database
@auth.get_password
def get_password(username):
    if username == 'tronza':
        return 'tronza'

    return None


# Recordar cambiar el código de error de 403 a 401 (cuando el servicio sea consumido por apps)
@auth.error_handler
def unauthorized():
    return make_response(jsonify({ 'error': 'Unauthorized access' } ), 403) 


app = Flask(__name__)

connect('tasks')

class Task(Document):
    id_num = IntField()
    title = StringField(required = True)
    description = StringField(max_length = 50)
    done =  BooleanField(default = False)

# Task.objects.delete()

# nueva_tarea = Task(id_num = 1)
# nueva_tarea.title = u'Comprar cosas'
# nueva_tarea.description = u'Milk, Cheese, Pizza, Fruit, Tylenol'
# nueva_tarea.save()

# db.task.remove()
# db.task.save(tasks[0])
# db.task.save(tasks[1])

@app.route('/api/v1/tasks', methods = ['GET'])
@auth.login_required
def get_tasks():
    salida = []
    tarea = Task.objects
    for t in tarea:
        item = {
            "title" : t.title,
            "description" : t.description,
            "done" : t.done,
            "id_num" : t.id_num
        }
        salida.append(item)

    return jsonify({'tareas': salida })



@app.route('/api/v1/tasks', methods = ['POST'])
def create_task():
    print request.json
    if not request.json or not 'title' in request.json:
        abort(400)

    new_task = Task()
    new_task.title = request.json['title']
    new_task.description = request.json.get('description', "")
    new_task.id_num = request.json['id_num']
    new_task.done = request.json.get('done', False)
    
    new_task.save()
    
    salida = []
    tarea = Task.objects
    for t in tarea:
        item = {
            "title" : t.title,
            "description" : t.description,
            "done" : t.done,
            "id_num" : t.id_num
        }
        salida.append(item)

    return jsonify({'tareas': salida }), 201



@app.route('/api/v1/tasks/<int:task_id>', methods = ['PUT'])
def update_task(task_id):
    print request.json
    
    try:
        to_update = Task.objects.get(id_num = task_id)
        print to_update.title
    except Exception, e:
        print e
        


    return jsonify({'tareas': False })

if __name__ == '__main__':
    app.run(debug = True)
