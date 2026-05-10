import os

import streamlit as st
import pickle
import pandas as pd
import requests
from dotenv import load_dotenv
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

def get_safe_session():
    session = requests.Session()
    retry = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
API_KEY = os.getenv("API_KEY")

session = get_safe_session()

movies = pd.DataFrame(movies_dict)

def fetch_movie_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=191521f05f4be6eba96004f8fde020ac"
    try:
        response = session.get(url, timeout=15)
        response.raise_for_status()
        print("Status Code:", response.status_code)

        # Raise error if request failed
        data = response.json()
        # print(data)   # Debugging

        poster_path = data['poster_path']
        return f"https://image.tmdb.org/t/p/w500/{poster_path}"

    except requests.exceptions.RequestException as e:
        print("Connection Error:", e)
        return "https://via.placeholder.com/500x750?text=Error"

def recommend(movie_name):
    movie_index = movies[movies['title'] == movie_name].index[0]
    distances = similarity[movie_index]
    # normal_list = [(idx, float(dist)) for idx, dist in distances]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        # fetch poster API
        recommended_movies_posters.append(fetch_movie_poster(movie_id))

    return recommended_movies, recommended_movies_posters

st.title("Movie Reccomender System")

selected_movie = st.selectbox(
    "Select a movie",
    movies['title'].values
)

if st.button("recommend"):
    st.subheader("Recommend Movie")
    movies, posters = recommend(selected_movie)
    # st.write(posters)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.text(movies[0])
        st.image(posters[0])
    with col2:
        st.text(movies[1])
        st.image(posters[1])
    with col3:
        st.text(movies[2])
        st.image(posters[2])
    with col4:
        st.text(movies[3])
        st.image(posters[3])
    with col5:
        st.text(movies[4])
        st.image(posters[4])
