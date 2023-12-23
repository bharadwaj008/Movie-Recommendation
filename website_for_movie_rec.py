# -*- coding: utf-8 -*-
"""
Created on Thu Dec 21 22:31:44 2023

@author: kamep
"""

import streamlit as st
import pandas as pd 
from scipy.sparse import csr_matrix
import pickle

movies = pd.read_csv("C:/Users/kamep/Documents/Github/Movie Recommendation/movie-lens-small-dataset/movies.csv")

ratings = pd.read_csv("C:/Users/kamep/Documents/Github/Movie Recommendation/movie-lens-small-dataset/ratings.csv")

final_dataset = ratings.pivot(index='movieId',columns='userId',values='rating')

final_dataset.fillna(0,inplace=True)

no_user_voted = ratings.groupby('movieId')['rating'].agg('count')

no_movies_voted = ratings.groupby('userId')['rating'].agg('count')

final_dataset = final_dataset.loc[no_user_voted[no_user_voted > 10].index,:]

final_dataset=final_dataset.loc[:,no_movies_voted[no_movies_voted > 50].index]

csr_data = csr_matrix(final_dataset.values)

final_dataset.reset_index(inplace=True)

model = pickle.load(open('C:/Users/kamep/Documents/Github/Movie Recommendation/movie_recommendation.sav','rb'))


def get_movie_recommendation1(movie_name):
    n_movies_to_reccomend = 10
    movie_list = movies[movies['title'].str.contains(movie_name,case = False , regex = False)]  
    if len(movie_list):        
        movie_idx= movie_list.iloc[0]['movieId']
        if final_dataset[final_dataset['movieId'] == movie_idx].empty:
            return '''To qualify a movie, minimum 10 users should have voted a movie.'''
        else: 
            movie_idx = final_dataset[final_dataset['movieId'] == movie_idx].index[0]
        
        distances , indices = model.kneighbors(csr_data[movie_idx],n_neighbors=n_movies_to_reccomend+1)    
        rec_movie_indices = sorted(list(zip(indices.squeeze().tolist(),distances.squeeze().tolist())),\
                               key=lambda x: x[1])[:0:-1]
        
        recommend_frame = []
        
        for val in rec_movie_indices:
            movie_idx = final_dataset.iloc[val[0]]['movieId']
            idx = movies[movies['movieId'] == movie_idx].index
            recommend_frame.append({'Title':movies.iloc[idx]['title'].values[0],'Distance':val[1]})
        df = pd.DataFrame(recommend_frame,index=range(1,n_movies_to_reccomend+1))
        return df
    
    else:
        
        return "No movies found. Please check your input"


# Set the title of the web application
st.title(" :movie_camera: Movie Similarity Recommender")

# Add a brief description of your system
st.write("Discover movies similar to your favorite! Select one or more movies from the list to get recommendations.")

# Load movie data (replace 'movies.csv' with the actual path to your MovieLens Small Dataset)
movie_data = pd.read_csv('C:/Users/kamep/Documents/Github/Movie Recommendation/movie-lens-small-dataset/movies.csv')


# Split the 'genres' column by '|'
#genres_split = movie_data['genres'].str.split('|', expand=True)

genres_split = movie_data['genres'].str.get_dummies('|')

# Concatenate the original DataFrame with the split genres
movie_data = pd.concat([movie_data, genres_split], axis=1)

print(genres_split.columns.tolist())

selected_genres = st.multiselect("Select one or more genres",genres_split.columns.tolist())

#genres = ['Action','Adventure']

#selected_movies = movie_data[movie_data[genres].any(axis=1)][['title'] + genres]

#print(selected_movies)

movies_list = movie_data[movie_data[selected_genres].any(axis=1)][['title']]
# Create a multiselect for searching and selecting movies
selected_movies = st.multiselect("Select one or more movies", movies_list)

# Display user input
if selected_movies:
    st.write(f"Movies similar to {', '.join(selected_movies)}: {selected_movies}")
    
    # Get similar movies for each selected movie
    for selected_movie in selected_movies:
        similar_movies = get_movie_recommendation1(selected_movie)  # Replace with your actual function
        st.subheader(f"Movies similar to '{selected_movie}':")
        
        if type(similar_movies) == str:
            st.write('To suggest a movie based on given movie, minimum 10 users should have voted that movie.')
        # Display similar movies
        elif similar_movies.empty:
            st.warning(f"No similar movies found for '{selected_movie}'.")
            
        else:
            st.table(similar_movies)  # Display top 10 similar movies
else:
    st.warning("Please select one or more movies to get recommendations.")
# Add a styled footer with a black background color
footer = """
<style>
.footer {
    background-color: #000;
    color: #fff;
    padding: 10px;
    text-align: center;
}
</style>

<div class="footer">
    <p>Dataset Link: <a href="https://www.kaggle.com/datasets/shubhammehta21/movie-lens-small-latest-dataset" target="_blank">Movie-lens small dataset </a></p>
    <p>Built with ❤️ by Bharadwaj</p>
</div>
"""
st.markdown(footer, unsafe_allow_html=True)


# Run the app with `streamlit run your_app_name.py` in the terminal
