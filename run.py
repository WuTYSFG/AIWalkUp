import os
import time
from datetime import datetime
from flask import Flask, render_template, send_from_directory, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy

import cv2
import mediapipe as mp

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

class BasicModel(object):
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate = datetime.now)

class User(BasicModel, db.Model):

    __tablename__ = 'user'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    phone_num = db.Column(db.String(20), unique=True, nullable=False)  
    password = db.Column(db.String(20), nullable=False)
    # age = db.Column(db.Integer, nullable=False) 
    # id_card = db.Column(db.String(18))
    # real_name = db.Column(db.String(10),nullable=False)

    #def __repr__(self) -> str:
    #    return super().__repr__()

class Video(db.Model):

    __tablename__ = 'video'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    #label = db.Column(db.String(20), nullable=False)
    video_path = db.Column(db.String(255), nullable=False) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) 

@app.route('/')
def hello_world():
    return 'hello world'

@app.route('/passport')
def passport():
    return render_template('passport.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/api/register', methods=['POST'], strict_slashes=False)
def api_register():
    req_dict = dict(request.form)
    phone_num = req_dict.get("phone_num")
    password = req_dict.get("password")
    password2 = req_dict.get("password2")

    if password != password2:
        return jsonify({"errno":1002,"errmsg": "The two entered passwords do not match"})
    
    u = User(phone_num=phone_num, password=password)

    db.session.add(u)

    db.session.commit()

    # return jsonify({"errno":0, "errmsg":"register successful", "phone_num":phone_num, "password":password})
    return render_template('login.html')


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/api/login', methods=['POST'], strict_slashes=False)
def api_login():
    req_dict = dict(request.form)
    phone_num = req_dict.get("phone_num")
    password = req_dict.get("password")

    user = User.query.get(1)
    if password == user.password:
        return render_template('upload.html')
    else:
        return jsonify({"errno":1003, "errmsg":"password error"})


def hand(url):
    # mp.solutions.drawing_utils用于绘制
    mp_drawing = mp.solutions.drawing_utils

    # 参数：1、颜色，2、线条粗细，3、点的半径
    DrawingSpec_point = mp_drawing.DrawingSpec((0, 255, 0), 1, 1)
    DrawingSpec_line = mp_drawing.DrawingSpec((0, 0, 255), 1, 1)

    # mp.solutions.hands，是人的手
    mp_hands = mp.solutions.hands

    # 参数：1、是否检测静态图片，2、手的数量，3、检测阈值，4、跟踪阈值
    hands_mode = mp_hands.Hands(max_num_hands=2)

    cap = cv2.VideoCapture(url)

    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    out = cv2.VideoWriter('out.mp4',fourcc, 20.0, (1280, 720))

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break
        
        image1 = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # 处理RGB图像
        results = hands_mode.process(image1)

        # 绘制

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                for id, lm in enumerate(hand_landmarks.landmark):
                    h, w, c = image1.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    print(id, cx, cy)
                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS, DrawingSpec_point, DrawingSpec_line)
        out.write(image)
        #cv2.imshow('MediaPipe Hands', image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    hands_mode.close()
    cap.release()
    out.release()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/api/upload', methods=['POST'], strict_slashes=False)
def api_upload():
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER']) 

    if not os.path.exists(file_dir):
        os.makedirs(file_dir)  
    
    f=request.files['myfile']

    if f and allowed_file(f.filename):
        fname=f.filename
        ext = fname.rsplit('.', 1)[1]  

        unix_time = int(time.time())

        new_filename = str(unix_time)+'.'+ext   

        path = os.path.join(file_dir, new_filename)
        f.save(path)

        v = Video(video_path=path, user_id=)

        db.session.add(v)

        db.session.commit()

        hand(path)

        return jsonify({"errno": 0, "errmsg": "upload successfully"})
        #return render_template('analyze.html')
    
    else:
        return jsonify({"errno": 1001, "errmsg": "upload failed"})
        
@app.route('/result')
def result():
    return render_template('result.html')

@app.route("/download/<path:filename>")
def downloader(filename):
    #dirpath = os.path.join(app.root_path, 'upload')
    return send_from_directory(app.root_path, filename, as_attachment=True) 

@app.route('/index')
def index():
    return render_template('index.html', username='wuty')  
if __name__ == "__main__":
    
    db.drop_all()

    db.create_all()
    
    app.run(host='127.0.0.1', port=8080) 