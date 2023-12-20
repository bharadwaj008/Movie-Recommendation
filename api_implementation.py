
import json
import requests
from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import pandas as pd

from scipy.sparse import csr_matrix

movies = pd.read_csv("movie-lens-small-dataset/movies.csv")

ratings = pd.read_csv("movie-lens-small-dataset/ratings.csv")

final_dataset = ratings.pivot(index='movieId',columns='userId',values='rating')

final_dataset.fillna(0,inplace=True)

no_user_voted = ratings.groupby('movieId')['rating'].agg('count')

no_movies_voted = ratings.groupby('userId')['rating'].agg('count')

final_dataset = final_dataset.loc[no_user_voted[no_user_voted > 10].index,:]

final_dataset=final_dataset.loc[:,no_movies_voted[no_movies_voted > 50].index]

csr_data = csr_matrix(final_dataset.values)

final_dataset.reset_index(inplace=True)




app = FastAPI()

class model_input(BaseModel):
    
    movie_name : str

movie_rec_model = pickle.load(open('movie_recommendation.sav','rb'))

@app.post('/movie-recommendation')
def get_movie_recommendation_api(input_parameters : model_input):
    n_movies_to_reccomend = 10
    input_data = input_parameters.json()
    input_dictionary = json.loads(input_data)
    movie_name = input_dictionary['movie_name']
    movie_list = movies[movies['title'].str.contains(movie_name,case = False)]  
    if len(movie_list):        
        movie_idx= movie_list.iloc[0]['movieId']
        movie_idx = final_dataset[final_dataset['movieId'] == movie_idx].index[0]
        
        distances , indices = movie_rec_model.kneighbors(csr_data[movie_idx],n_neighbors=n_movies_to_reccomend+1)    
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
