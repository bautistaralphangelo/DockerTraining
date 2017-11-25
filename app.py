from flask import Flask, redirect, url_for, \
				  request, render_template, json
from pymongo import MongoClient
import pymongo
import os
import socket
from bson import ObjectId



class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


client = MongoClient('mongodb://backend:3306/dockerdemo')
db = client.blogpostDB

app = Flask(__name__)

@app.route("/")
def landing_page():
    posts = get_all_posts()

    return render_template('blog.html', posts=json.loads(posts))


@app.route('/add_post', methods=['POST'])
def add_post():

    new()
    return redirect(url_for('landing_page'))


@app.route('/remove_all')
def remove_all():
    db.blogpostDB.delete_many({})

    return redirect(url_for('landing_page'))




## Services

@app.route("/posts", methods=['GET'])
def get_all_posts():

    _posts = db.blogpostDB.find()
    posts = [post for post in _posts]
    return JSONEncoder().encode(posts)


@app.route('/new', methods=['POST'])
def new():

    item_doc = {
        'title': request.form['title'],
        'post': request.form['post']
    }
    db.blogpostDB.insert_one(item_doc)

    _posts = db.blogpostDB.find()
    posts = [post for post in _posts]

    return JSONEncoder().encode(posts[-1])


### Insert function here ###
@app.route('/post_get', methods=['GET'])
def post_get():
    post = get_post()

    return render_template('edit_blog.html', post=json.loads(post))

@app.route('/post_update', methods=['POST'])
def post_update():
    update_post()

    return redirect(url_for('landing_page'))


@app.route('/post_delete', methods=['GET'])
def post_delete():
    delete_post()

    return redirect(url_for('landing_page'))


@app.route('/post/get', methods=['GET'])
def get_post():
    post_id = request.args.get('id')
    post = db.blogpostDB.find_one({'_id' : ObjectId(post_id)})

    return JSONEncoder().encode(post)

@app.route('/post/update', methods=['POST'])
def update_post():
    post_id = request.form['id']
    post = {
        'title': request.form['title'],
        'post': request.form['post']
    }

    update_result = db.blogpostDB.update_one({'_id' : ObjectId(post_id)}, {'$set' : post})
    response = {
        'modified_count': update_result.matched_count
    }

    return JSONEncoder().encode(response)

@app.route('/post/delete', methods=['GET'])
def delete_post():
    post_id = request.args['id']

    delete_result = db.blogpostDB.delete_one({'_id' : ObjectId(post_id)})

    response = {
        'deleted_count': delete_result.deleted_count
    }

    return JSONEncoder().encode(response)
############################



if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
