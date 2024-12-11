from flask import Flask, render_template, url_for,request, jsonify, session,redirect, flash
from pymongo import MongoClient
import sys
import os
from datetime import datetime
# Thêm thư mục gốc vào sys.path để Python có thể tìm thấy thư mục model
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from model.RecommendationSystem import Recommendation
import pandas as pd

app = Flask(__name__)
recommendation = Recommendation()
df = pd.read_csv("model\Coursera.csv")
data = recommendation.pre_processing(df)
data['tags'] = data['tags'].apply(recommendation.stem)
uri = "mongodb+srv://tnchau23823:abc13579@cluster0.fs6jd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)

app.secret_key = 'key'  # Required for session management
db = client['my_database']
db_courses = db['db_courses']
accounts = db['account']
searchs = db['search']
views = db['view']
@app.route('/')
def home():
    return render_template("home.html")


@app.route('/login', methods = ['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        
        user = accounts.find_one({'username': username, 'password': password})
        if user:
            session['username'] = username
            flash('Đăng nhập thành công!', 'success')
            return render_template("home.html")
        else:
            return render_template('login.html',message='Tên đăng nhập hoặc mật khẩu không đúng')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)  # Xóa session khi logout
    return render_template('login.html',message='Bạn đã đăng xuất thành công')


@app.route('/handle_click', methods=['POST'])
def handle_click():
    clicked_item = request.json.get('clicked_item')
    if not clicked_item:
        return jsonify({'message': 'No action provided'}), 400  # Trả về lỗi nếu không nhận được dữ liệu

    if clicked_item == 'profile':
        response = "Profile icon clicked!"
    else:
        response = "Unknown action."

    return jsonify({'message': response})


@app.route('/course/<course_id>', methods=['GET'])
def view_course(course_id):
    course = db_courses.find_one({"Course ID": course_id})
    if not course:
        return "Course not found", 404

    if 'username' in session:
        username = session['username']
        views.insert_one({
            'course_id': course_id,
            'username': username,
            'time': datetime.now()
        })

    # Chuyển hướng đến URL của khóa học
    return redirect(course["Course URL"])


@app.route('/explore', methods=['POST'])
def explore():
    # Lấy giá trị từ ô nhập liệu
    user_input = request.form.get('query')
    if 'username' in session:
        username =  session['username']
        searchs.insert_one({'query': user_input, 'username' : username, 'time_query': datetime.now()})
    recommendations = recommendation.recommend(user_input, data)
    course_list = []
    for course_name in recommendations:
        # Tìm khóa học trong MongoDB theo tên
        course = db_courses.find_one({"Course Name": course_name})        
        if course:
            course_list.append({
                "name": course["Course Name"],
                "url": url_for('view_course', course_id=course["Course ID"]),
                "course_id": course["Course ID"]
            })
    # print(course_list)
    return render_template('explore.html', courses=course_list)


if __name__ == "__main__":
    app.run()