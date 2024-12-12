import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem.porter import PorterStemmer

class Recommendation:
    def __init__(self, data: dict):
        self.data = self._preprocess_data(data)

    def _clean_columns(self, data, columns):
        """
        Làm sạch các cột chỉ định trong DataFrame, thay thế ký tự không mong muốn.
        """
        for column in columns:
            if column in data.columns:
                self.data[column] = self.data[column].str.replace(r"[,:_()]", "", regex=True)
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

    def user_search(self, user_input, data, number_course_recommend=6):
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
        if 'tags' not in data.columns or 'course_name' not in data.columns:
            raise ValueError("Dữ liệu cần có các cột 'tags' và 'course_name'.")

        # Chuẩn bị dữ liệu
        data = data.copy()
        data['tags'] = data['tags'].str.lower()

        # Thêm input từ người dùng vào dataset để tính toán
        data = pd.concat([data, pd.DataFrame({'tags': [user_input.lower()], 'course_name': ['User Input']})], ignore_index=True)

        # Vector hóa văn bản
        cv = CountVectorizer(max_features=5000, stop_words='english')
        vectors = cv.fit_transform(data['tags']).toarray()
        
        # Tính độ tương đồng cosine
        similarity = cosine_similarity(vectors)

        # Lấy chỉ số của user input
        user_index = data[data['course_name'] == 'User Input'].index[0]

        # Lấy danh sách các khóa học tương tự
        distances = similarity[user_index]
        recommended_indices = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:number_course_recommend + 1]

        # Trả về thông tin khóa học được gợi ý
        recommendations = []
        for idx, _ in recommended_indices:
            course = data.iloc[idx]
            # print(course)
            recommendations.append(course['course_name'])
                # 'description': course.get('description', 'No description available'),
                # 'url': course.get('url', '#')  # URL khóa học (nếu có)
            # })

        return recommendations

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
        