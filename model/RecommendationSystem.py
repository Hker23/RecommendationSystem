import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem.porter import PorterStemmer
from pymongo import MongoClient
uri = "mongodb+srv://tnchau23823:abc13579@cluster0.fs6jd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)
db = client['my_database']
db_courses = db['db_courses']


class Recommendation:
    def __init__(self):
        pass
    def history_data(self, username, number_courses, data):
        """
        Tạo danh sách ngẫu nhiên các khóa học từ dữ liệu đầu vào.
        """
        if 'course_name' not in data.columns:
            raise ValueError("Dữ liệu đầu vào thiếu cột 'course_name'.")
        return data['course_name'].sample(n=number_courses, random_state=42)

    def clean_columns(self, data, columns):
        """
        Làm sạch các cột chỉ định trong DataFrame, thay thế ký tự không mong muốn.
        """
        for column in columns:
            if column in data.columns:
                data[column] = data[column].str.replace(r"[,:_()]", "", regex=True)
        return data

    def pre_processing(self, data):
        """
        Tiền xử lý dữ liệu: Làm sạch và tạo cột `tags` kết hợp thông tin cần thiết.
        """
        required_columns = ['Course Name', 'Course Description', 'Skills', 'Difficulty Level']
        for col in required_columns:
            if col not in data.columns:
                raise ValueError(f"Dữ liệu thiếu cột '{col}'.")

        # Làm sạch dữ liệu
        data_clean = self.clean_columns(data, ['Course Name', 'Course Description', 'Skills'])
        
        # Kết hợp các cột tạo thành `tags`
        data_clean['tags'] = (
            data_clean['Course Name'] + " " +
            data_clean['Difficulty Level'] + " " +
            data_clean['Course Description'] + " " +
            data_clean['Skills']
        ).str.lower()

        # Lựa chọn các cột cần thiết
        new_data = data_clean[['Course Name', 'tags']].rename(columns={'Course Name': 'course_name'})
        
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

    def recommend(self, user_input, data, number_course_recommend=6):
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
    
    
    def recommend_with_rating(self, courses, data, number_course_recommend=6, rating_weight=0.5):
        """
        Đề xuất khóa học dựa trên cột 'rating' và 'cosine_similarity'.

        Parameters:
            courses: Danh sách tên các khóa học đã chọn.
            data: DataFrame chứa thông tin khóa học (phải có 'course_name', 'tags', và 'rating').
            number_course_recommend: Số lượng khóa học gợi ý (mặc định 6).
            rating_weight: Trọng số để ưu tiên cột rating (0 đến 1).
        
        Returns:
            Danh sách tên các khóa học được đề xuất.
        """
        # Kiểm tra các cột cần thiết
        required_columns = {'course_name', 'tags', 'rating'}
        if not required_columns.issubset(data.columns):
            raise ValueError(f"Dữ liệu đầu vào thiếu một trong các cột: {required_columns}")

        # Tính ma trận tương đồng
        similarity = self.similarity_measure(data)

        # Lấy chỉ số các khóa học đầu vào
        course_indices = [
            data[data['course_name'] == course].index[0] 
            for course in courses if course in data['course_name'].values
        ]
        if not course_indices:
            raise ValueError("Không có khóa học nào hợp lệ trong danh sách đầu vào.")

        # Tính tổng điểm tương đồng
        combined_distances = np.mean([similarity[idx] for idx in course_indices], axis=0)

        # Chuẩn hóa điểm rating
        data['rating_normalized'] = (data['rating'] - data['rating'].min()) / (data['rating'].max() - data['rating'].min())

        # Tạo điểm tổng hợp với rating
        combined_scores = (1 - rating_weight) * combined_distances + rating_weight * data['rating_normalized']

        # Sắp xếp khóa học dựa trên điểm tổng hợp
        recommended_courses = sorted(
            enumerate(combined_scores),
            key=lambda x: x[1],
            reverse=True
        )

        # Loại bỏ các khóa học đã chọn
        recommended_courses = [
            data.iloc[i[0]].course_name for i in recommended_courses 
            if i[0] not in course_indices
        ][:number_course_recommend]

        return recommended_courses


