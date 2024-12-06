from flask import Flask, render_template, url_for,request
from pymongo import MongoClient
import sys
import os

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

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/explore', methods=['POST'])
def explore():
    # Lấy giá trị từ ô nhập liệu
    user_input = request.form.get('query')
    recommendations = recommendation.recommend(user_input, data)
    course_list = []
    for course_name in recommendations:
        # Tìm khóa học trong MongoDB theo tên
        course = db_courses.find_one({"Course Name": course_name})        
        if course:
            course_list.append({
                "name": course["Course Name"],
                "url": course["Course URL"]
            })
    # print(course_list)
    return render_template('explore.html', courses=course_list)


if __name__ == "__main__":
    app.run()