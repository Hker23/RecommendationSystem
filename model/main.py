# from RecommendationSystem import Recommendation
import os
import pandas as pd
import uuid
import numpy as np
from dotenv import load_dotenv
from pymongo import MongoClient
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)
db = client['my_database']
db_courses = db['db_courses']
Course_ID = "6b645dfc-128d-426a-b6c5-138cffb36c62"
data = pd.read_csv("Coursera.csv")
def score_wordbase_view(course_id, data):
    # Tìm khóa học trong cơ sở dữ liệu
    document = db_courses.find_one({'Course ID': course_id})
    if not document:
        raise ValueError(f"Course with ID {course_id} not found")

    # Mô tả khóa học cần so sánh
    course_description = document["Course Description"]

    # Tất cả mô tả khóa học
    course_descriptions = data['Course Description']

    #Vectorizer
    cv = CountVectorizer(max_features=5000, stop_words='english')
    vectors = cv.fit_transform(course_descriptions)

    # Tính vector cho khóa học cần so sánh
    query_vector = cv.transform([course_description])

    # Tính tương đồng cosine
    similarity_scores = cosine_similarity(query_vector, vectors)

    # Trả về điểm tương đồng
    return similarity_scores.flatten()

similarity_scores = score_wordbase_view(Course_ID, data)





# def calculate_similarity(query, course_descriptions):
#     # Tạo vector hóa TF-IDF
#     tfidf = TfidfVectorizer(max_features=5000, stop_words='english')
    
#     # Kết hợp query với các mô tả khóa học
#     all_texts = [query] + course_descriptions
    
#     # Vector hóa toàn bộ
#     vectors = tfidf.fit_transform(all_texts)
    
#     # Vector của query
#     query_vector = vectors[0]
    
#     # Vectors của các mô tả khóa học
#     course_vectors = vectors[1:]
    
#     # Tính toán tương đồng cosine
#     similarities = cosine_similarity(query_vector, course_vectors)
    
#     # Trả về danh sách điểm tương đồng
#     return similarities.flatten()

# Ví dụ dữ liệu
# query = "design, business, english"
# course_descriptions = [
#     "Learn English for business communication",
#     "Introduction to graphic design",
#     "Advanced business management course"
# ]

# # Tính toán
# similarity_scores = calculate_similarity(query, course_descriptions)

# # In kết quả
# for i, score in enumerate(similarity_scores):
#     print(f"Course {i}: Similarity = {score:.2f}")



# Mô phỏng dữ liệu khóa học
# courses = [
#     {"id": 1, "name": "Python for Beginners", "description": "Learn Python from scratch."},
#     {"id": 2, "name": "Data Science", "description": "Introduction to data analysis and machine learning."},
#     {"id": 3, "name": "Web Development", "description": "Build modern websites with HTML, CSS, and JavaScript."},
# ]
courses = pd.read_csv("model\\Coursera.csv")

# print(document["Course Description"])
# # Hàm để tính score dựa trên description
# def calculate_description_score(query, descriptions):
#     vectorizer = TfidfVectorizer()
#     vectors = vectorizer.fit_transform(descriptions + [query])  # Bao gồm cả query
#     query_vector = vectors[-1]  # Vector của query
#     description_vectors = vectors[:-1]  # Các vector của descriptions

#     scores = cosine_similarity(query_vector, description_vectors).flatten()  # Tính cosine similarity
#     return scores

# # Hàm để tính score dựa trên query (tương tự description nhưng có thể dùng thêm trọng số nếu cần)
# def calculate_query_score(query, data):
#     cv = CountVectorizer(max_features=5000, stop_words='english')
#     vectors = cv.fit_transform(data['tags']).toarray()
#     query_vector = vectors[-1]  # Vector của query
#     course_name_vectors = vectors[:-1]

#     scores = cosine_similarity(query_vector, course_name_vectors).flatten()
#     return scores

# Hàm để tính tổng điểm và recommend
# weights: description_weight = 0.3, query_weight = 0.7 (theo sơ đồ)
# def recommend_courses(query, courses, description_weight=0.3, query_weight=0.7, top_k=3):
#     descriptions = courses['Course Description'].to_list()
#     course_names = courses['Course Name'].to_list()

#     # Tính điểm cho description và query
#     description_scores = calculate_description_score(query, descriptions)
#     query_scores = calculate_query_score(query, course_names)

#     # Tổng điểm có trọng số
#     total_scores = description_weight * description_scores + query_weight * query_scores

#     # Sắp xếp các khóa học theo tổng điểm
#     ranked_courses = sorted(
#         zip(courses, total_scores), key=lambda x: x[1], reverse=True
#     )

#     # Chỉ lấy top_k khóa học
#     recommended_courses = ranked_courses[:top_k]
#     return [course for course, score in recommended_courses]

# Ví dụ sử dụng
# user_query = "Learn programming and data analysis"
# recommended = recommend_courses(user_query, courses)

temp = set()
courses.drop_duplicates(subset='Course URL', inplace=True)
courses.to_csv("model\\clean.csv", index=False)
# print("Recommended Courses:")
# print(recommended)
    # print(f"- {course['Course Name']}: {course['Course Description']}")

# Read csv
# df = pd.read_csv("Coursera.csv")
# df["course_id"] = [str(uuid.uuid4()) for _ in range(len(df))]

# print(df.head())
# from pymongo import MongoClient

# # Kết nối tới MongoDB Cloud
# def connect_to_mongodb(uri, database_name, collection_name):
#     client = MongoClient(uri)
#     db = client[database_name]
#     collection = db[collection_name]
#     return collection

# # Đọc file CSV và lưu vào MongoDB
# def save_csv_to_mongodb(csv_file, collection, selected_columns):
#     # Đọc file CSV
#     data = pd.read_csv(csv_file)
#     data["Course ID"] = [str(uuid.uuid4()) for _ in range(len(data))]
#     # Chọn các cột cần thiết
#     if selected_columns:
#         data = data[selected_columns]
    
#     # Chuyển dữ liệu thành dictionary
#     records = data.to_dict(orient='records')
    
#     # Thêm dữ liệu vào MongoDB
#     if records:
#         collection.insert_many(records)
#         print(f"Đã lưu {len(records)} bản ghi vào MongoDB.")
#     else:
#         print("Không có dữ liệu để lưu.")

# # Thông tin MongoDB và file CSV
# MONGO_URI = "mongodb+srv://tnchau23823:abc13579@cluster0.fs6jd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# DATABASE_NAME = "my_database"
# COLLECTION_NAME = "db_courses"
# CSV_FILE = "Coursera.csv"

# # Thực thi
# if __name__ == "__main__":
#     # Kết nối tới MongoDB
#     collection = connect_to_mongodb(MONGO_URI, DATABASE_NAME, COLLECTION_NAME)
    
#     # Lưu file CSV vào MongoDB
#     save_csv_to_mongodb(CSV_FILE, collection, selected_columns=["Course Name","University","Difficulty Level","Course Rating", "Course URL","Course Description","Skills","Course ID"])

