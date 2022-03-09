import os
from datetime import datetime
from flask import Flask, render_template, send_from_directory, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

user='root'
password='181257'
database='parkinson'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://%s:%s@127.0.0.1:3306/%s' % (user,password,database)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['UPLOAD_FOLDER'] = 'upload'
basedir = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = set(['txt', 'png', 'PNG', 'jpg', 'JPG', 'mp4'])

db = SQLAlchemy(app)

#class BasicModel(object):
    #create_time = db.Column(db.DateTime, default=datetime.now)
    #update_time = db.Column(db.DateTime, default=datetime.now, onupdate = datetime.now)

class User(db.Model):

    __tablename__ = 'user'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    phone_num = db.Column(db.String(20), unique=True, nullable=False)  
    password = db.Column(db.String(20), nullable=False)
    #age = db.Column(db.Integer, nullable=False) 

db.drop_all()

db.create_all()

u = User(phone_num='123', password='123456')

db.session.add(u)

db.session.commit()

app.run()