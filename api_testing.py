# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 12:20:06 2023

@author: kamep
"""

import json
import pandas as pd
import requests

url = 'http://127.0.0.1:8000/movie-recommendation'

input_data = {'movie_name' : 'jurassic park'}

input_json = json.dumps(input_data)

response = requests.post(url,data= input_json)

if response.text == "No movies found. Please check your input":
    
    print(response.text)

else:
    
    print(pd.DataFrame(json.loads(response.text)))

#print(pd.read_json(response.text))

#we can either use read_json method of pandas or
#convert the json to dict and use DataFrame method of pandas
