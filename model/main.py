from RecommendationSystem import Recommendation
import pandas as pd
# Read csv
df = pd.read_csv("Coursera.csv")



# Create object
recommendation = Recommendation()

# # Pre_processing data
data = recommendation.pre_processing(df)

# # Những khóa học đùng để recommend
# courses_to_recommend = recommendation.history_data("Chau",5,data)
topic = "Machine Learning"

print("Các khóa học đầu vào:", topic)
number_course_recommend = 6
# Recommem
recommendations = recommendation.recommend_by_topic(topic, data, number_course_recommend)
print("Khóa học gợi ý:", recommendations)

# # Recommend with rating
# rating = df['Course Rating']
# data['rating'] = rating
# # Convert 'rating' to numeric, replacing invalid entries with NaN
# data['rating'] = pd.to_numeric(data['rating'], errors='coerce')

# # Handle missing values (e.g., from 'Not Calibrated')
# data['rating'].fillna(data['rating'].mean(), inplace=True)

# rating_weight = 0.4
# recommendations_with_rating = recommendation.recommend_with_rating(courses_to_recommend, data, number_course_recommend, rating_weight)
# print("Khóa học gợi ý khi dùng rating:", recommendations)

