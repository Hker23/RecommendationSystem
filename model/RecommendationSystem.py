import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem.porter import PorterStemmer
from pymongo import MongoClient
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)
db = client['my_database']
db_courses = db['db_courses']


class Recommendation:
    def __init__(self, data: dict):
        self.data = self._preprocess_data(data)

    def _clean_columns(self, data, columns):
        """
        Làm sạch các cột chỉ định trong DataFrame, thay thế ký tự không mong muốn.
        """
        for column in columns:
            if column in data.columns:
                data[column] = data[column].str.replace(r"[,:_()]", "", regex=True)
        return data

    def _preprocess_data(self, data):
        """
        Tiền xử lý dữ liệu: Làm sạch và tạo cột `tags` kết hợp thông tin cần thiết.
        """
        required_columns = ['Course Name', 'Course Description', 'Skills', 'Difficulty Level']
        for col in required_columns:
            if col not in data.columns:
                raise ValueError(f"Dữ liệu thiếu cột '{col}'.")

        # Làm sạch dữ liệu
        data_clean = self._clean_columns(data, ['Course Name', 'Course Description', 'Skills'])

        # Kết hợp các cột tạo thành `tags`
        data_clean['tags'] = (
            data_clean['Course Description'] + " " +
            data_clean['Skills']
        ).str.lower()

        # Lựa chọn các cột cần thiết
        new_data = data_clean.rename(columns={
            'Course Name': 'course_name',
            'Skills': 'skills',
            'Course Description': 'description',
            'University': 'university',
            'Difficulty Level': 'difficulty',
            
        })

        # Giữ dấu cách giữa các từ trong `course_name`
        new_data['course_name'] = new_data['course_name'].str.strip()

        return new_data
    def stem(self,text):
        ps = PorterStemmer()
        y=[]
        for i in text.split():
            y.append(ps.stem(i))

        return " ".join(y)

    def similarity_measure(self, data):
        """
        Tính toán ma trận tương đồng cosine từ dữ liệu.
        """
        cv = CountVectorizer(max_features=5000, stop_words='english')
        vectors = cv.fit_transform(data['tags']).toarray()

        return cosine_similarity(vectors)

    def user_search(self, user_input, number_course_recommend=6):
        """
        Gợi ý các khóa học dựa trên input từ người dùng và dữ liệu khóa học.

        Parameters:
            user_input (str): Từ khóa hoặc chủ đề mà người dùng nhập vào.
            data (pd.DataFrame): Dataset chứa thông tin các khóa học. Phải có cột `tags` và `course_name`.
            number_course_recommend (int): Số lượng khóa học muốn gợi ý (mặc định là 6).

        Returns:
            list: Danh sách từ điển chứa tên, mô tả, URL khóa học.
        """
        # Kiểm tra cột cần thiết
        if 'tags' not in self.data.columns or 'course_name' not in self.data.columns:
            raise ValueError("Dữ liệu cần có các cột 'tags' và 'course_name'.")
        data = self.data.copy()
        data['tags'] = data['tags'].str.lower()

        data = pd.concat([data, pd.DataFrame({'tags': [user_input.lower()], 'course_name': ['User Input']})], ignore_index=True)
        cv = CountVectorizer(max_features=5000, stop_words='english')
        vectors = cv.fit_transform(data['tags']).toarray()
        similarity = cosine_similarity(vectors)

        user_index = data[data['course_name'] == 'User Input'].index[0]
        distances = similarity[user_index]
        recommended_indices = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:number_course_recommend + 1]

        recommendations = []
        for idx, _ in recommended_indices:
            course = self.data.iloc[idx]
            recommendations.append(course['course_name'])

        return recommendations

    def score_wordbase_view(self, course_id, data):
        # Tìm khóa học trong cơ sở dữ liệu
        document = db_courses.find_one({'Course ID': course_id})
        if not document:
            raise ValueError(f"Course with ID {course_id} not found")

        # Mô tả khóa học cần so sánh
        course_description = document["Course Description"]

        # Tất cả mô tả khóa học
        course_descriptions = data['Course Description'].str.lower()

        #Vectorizer
        cv = CountVectorizer(max_features=5000, stop_words='english')
        vectors = cv.fit_transform(course_descriptions)

        # Tính vector cho khóa học cần so sánh
        query_vector = cv.transform([course_description])

        # Tính tương đồng cosine
        similarity_scores = cosine_similarity(query_vector, vectors)

        # Trả về điểm tương đồng
        return similarity_scores.flatten()


    def score_wordbase_search(self, query, data):
        # Tất cả mô tả khóa học
        course_descriptions = data['Course Description'].str.lower()
        #Vectorizer
        cv = CountVectorizer(max_features=5000, stop_words='english')
        all_texts = [query] + course_descriptions
        vectors = cv.fit_transform(all_texts)
         # Vector của query
        query_vector = vectors[0]

        # Vectors của các mô tả khóa học
        course_vectors = vectors[1:]

        # Tính toán tương đồng cosine
        similarities = cosine_similarity(query_vector, course_vectors)

        # Trả về danh sách điểm tương đồng
        return similarities.flatten()

    def _score_semantic(self, course_ids: list, data: dict) -> list[float]:
        historical_data = []
        for course_id in course_ids:
            historical_data.append(data)

    def _score_wordbase_view(self, course_ids: list, data: dict) -> list[float]:
        pass

    def _score_wordbase_search(self, query: str, data: dict) -> list[float]:
        pass

    def _score_levenshtein(self, query: str, data: dict) -> list[float]:
        pass

    def _calculate_final_score(self, semantic_scores: list, wordbase_scores: list, levenshtein_scores: list):
        pass

    def recommend_with_rating(self, courses, data, number_course_recommend=6):
        """Recommend k courses with the historical data

        Args:
            courses (list): list of courses' name or infor
            data (dict): dictionary containing all data about courses
            number_course_recommend (int, optional): number of recommended courses. Defaults to 6.
        """
        