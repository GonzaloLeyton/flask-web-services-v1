#!flask/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request, make_response, abort
from flask.ext.mongoengine import MongoEngine
from flask.ext.httpauth import HTTPBasicAuth
from mongoengine import *
import pymongo, os, json, uuid, hashlib

app = Flask(__name__)
auth = HTTPBasicAuth()


# Nos conectamos a la base de datos y 
# creamos los documentos que utilizaremos 

connect('tasks')

class Task(Document):
    id_num = IntField()
    title = StringField(required = True)
    description = StringField(max_length = 50)
    done =  BooleanField(default = False)

class User(Document):
    name = StringField(required = True, unique=True)
    password = StringField(required = True)



# encriptamos la contraseña que está ingresando, para compararla con la del usuario
@auth.verify_password
def verify_password(username, password):
    try:
        user = User.objects.get(name = username)

        resp = check_password(user.password, password)

    except Exception, e:
        return False

    return resp



# Recordar cambiar el código de error de 403 a 401 (cuando el servicio sea consumido por apps)
@auth.error_handler
def unauthorized():
    return make_response(jsonify({ 'error': 'Unauthorized access' } ), 403) 



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



@app.route('/api/v1/users', methods = ['POST'])
def create_user():

    print request.json
    if not request.json or not 'name' in request.json:
        abort(400)

    new_user = User()
    new_user.name = request.json['name']
    new_user.password = hash_password(request.json['password'])

    # Controlamos error en caso de que se inserte un usuario que ya existe
    try:
        new_user.save()
    except Exception, e:
        print e
        abort(400)
    
    salida = []
    usuarios = User.objects
    for u in usuarios:
        item = {
            "name" : u.name,
            "password" : u.password
        }
        salida.append(item)

    return jsonify({'users': salida }), 201



####### Funciones para manipulas contraseñas #############

def hash_password(password, new_salt = False):
    # uuid is used to generate a random number
    salt = uuid.uuid4().hex
    if new_salt:
        salt = new_salt

    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt
    
def check_password(hashed_password, user_password):
    password, salt = hashed_password.split(':')
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()
 

if __name__ == '__main__':
    app.run(debug = True)
