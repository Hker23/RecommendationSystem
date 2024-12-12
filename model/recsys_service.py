import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
# from nltk.stem.porter import PorterStemmer
from pymongo import MongoClient
from levenshtein_service import LevenshteinService
from qdrant_service import QdrantService
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)
db = client['my_database']
db_courses = db['db_courses']

class RecommendationService():
    def __init__(self, data: dict):
        self.data = self._preprocess_data(data)
        self.vectorizer = CountVectorizer(max_features=5000, stop_words='english')
        self.data_vectors = self.vectorizer.fit_transform(self.data['tags'])
        self.levenshtein = LevenshteinService()
        self.semantic_model = SentenceTransformer(os.getenv("MODEL_PATH"))
        self.qdrant = QdrantService()

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
        data_clean = self._clean_columns(data, ['Course Name', 'Course Description', 'Skills'])
        data_clean['tags'] = (
            data_clean['Course Description'] + " " +
            data_clean['Skills']
        ).str.lower()
        new_data = data_clean.rename(columns={
            'Course Name': 'course_name',
            'Skills': 'skills',
            'Course Description': 'description',
            'University': 'university',
            'Difficulty Level': 'difficulty',
        })
        new_data['course_name'] = new_data['course_name'].str.strip()
        return new_data

    def _score_semantic(self, course_ids: list) -> list[float]:
        # similarity_scores_list = []
        for course_id in course_ids:
            document = db_courses.find_one({'Course ID': course_id})
            if document:
                historical_content = document["Course Description"]  # FIX
                query_vector = self.semantic_model.encode(historical_content)
                related_courses = self.qdrant.search_vectors(
                    collection_name="semantic",
                    query_vector=query_vector,
                    top_k = 100
                )
        #         similarity_scores_list.append(cosine_similarity(query_vector, self.data_vectors))
        # similarity_scores = np.mean(np.array(similarity_scores_list), axis=0)
        # return similarity_scores.flatten()
        return related_courses

    def _score_wordbase_view(self, course_ids: list[str]) -> np.ndarray:
        similarity_scores_list = []
        for course_id in course_ids:
            document = db_courses.find_one({'Course ID': course_id})
            if document:
                historical_content = document["Course Description"]  # FIX
                query_vector = self.vectorizer.transform([historical_content])
                similarity_scores_list.append(cosine_similarity(query_vector, self.data_vectors))
        similarity_scores = np.mean(np.array(similarity_scores_list), axis=0)
        return similarity_scores.flatten()

    def _score_wordbase_search(self, queries: list[str]) -> np.ndarray:
        similarity_scores_list = []
        for query in queries:
            query_vector = self.vectorizer.transform([query])
            similarity_scores_list.append(cosine_similarity(query_vector, self.data_vectors))
        similarity_scores = np.mean(np.array(similarity_scores_list), axis=0)
        return similarity_scores.flatten()

    def _score_wordbase(self, course_ids: list, queries: list):
        return self._score_wordbase_search(queries) * 0.6 + self._score_wordbase_view(course_ids) * 0.4

    def _score_levenshtein(self, queries: list[str]) -> list[float]:
        similarity_scores_list = []
        for query in queries:
            similarity_scores_list.append(self.levenshtein.bulk_similarity(query, self.data["course_name"]))
        similarity_scores = np.mean(np.array(similarity_scores_list), axis=0)
        return similarity_scores.flatten()

    def _calculate_final_score(self, course_ids: list, queries: list):
        return (
            self._score_levenshtein(queries) * 0.1 +
            self._score_wordbase(course_ids=course_ids, queries=queries) * 0.9
        )

    def recommend_with_rating(self, username: str, number_course_recommend=6):
        """Recommend k courses with the historical data of user

        Args:
            username (str): username
            number_course_recommend (int, optional): number of recommended courses. Defaults to 6.
        """
        pass
