import pandas as pd
import numpy as np
from joblib import dump, load
import gradio as gr
import requests

cosine_similarities = load('/model/cosine_similarities.joblib') 
data_clean = load("/model/data_clean.joblib")

notFound = "https://upload.wikimedia.org/wikipedia/commons/6/64/Poster_not_available.jpg"

def recommendations(id, count=10):
    # Get the pairwsie similarity scores of all movies with that movie
    sim_scores = list(enumerate(cosine_similarities[id]))

    # Sort the movies based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores of the 10 most similar movies
    sim_scores = sim_scores[1:count+1]

    # Get the movie indices
    movie_indices = [i[0] for i in sim_scores]

    # Return the top 10 most similar movies
    return data_clean.iloc[movie_indices]

def netflix(title):
    # find the name in the list
    names = data_clean[data_clean['title'].str.contains(title, case=False)]
    if int(names.shape[0]) > 0:
        # Content is found
        # get an image for it
        
        img = notFound
        title = str(names['title'].iloc[0])
        
        response = requests.get("https://api.themoviedb.org/3/search/multi?api_key=15d2ea6d0dc1d476efbca3eba2b9bbfb&query=" + str(names['title'].iloc[0]))
        if response.json()["total_results"] > 0:
            if response.json()["results"][0]["poster_path"] != None:
                img = "http://image.tmdb.org/t/p/w500" + str(response.json()["results"][0]["poster_path"])
            elif response.json()["results"][0]["backdrop_path"] != None:
                img = "http://image.tmdb.org/t/p/w500" + str(response.json()["results"][0]["backdrop_path"])
        
        # get the 10 commendations
        recs = recommendations(names.index.values[0])
        
        html = ""
        
        count_l = 1
        
        for index, row in recs.iterrows():
            if str(row['imdb_id']) != 'nan':
                html+="<p><a target='_blank' href='https://imdb.com/title/" + str(row['imdb_id']) + "'>" + str(count_l) + ". " + row['title'] + "</a></p>"
            else:
                html+="<p>" + str(count_l) + ". " + row['title'] + "</p>"
            count_l+=1
        
        return ("Recommendations for " + title, img, "<div>" + html + "</div>")
        #return ("Recommendations for " + title, "<div>" + html + "</div>")
        
    return ("Not found in dataset", notFound, "")
    #return ("Not found in dataset", "")

demo = gr.Interface(
    fn=netflix,
    inputs=gr.Textbox(lines=2, placeholder="TV show or movie name here..."),
    outputs=["text","image", "html"],
    #outputs=["text", "html"],
    examples=[
        ["Disenchantment"],
        ["Enola Holmes"],
        ['The Dark Knight Rises'],
    ]
)

demo.launch(server_name="0.0.0.0", server_port=5000)