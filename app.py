from flask import Flask, render_template, request, redirect
import pickle
import requests
import os

app = Flask(__name__)

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url).json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

def recommend(movie):
    movies = pickle.load(open('movie_list.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        # fetch the movie poster
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
    return recommended_movie_names, recommended_movie_posters

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        selected_movie = request.form['movie']
        return redirect(f'/recommendations/{selected_movie}')
    else:
        movies = pickle.load(open('movie_list.pkl', 'rb'))
        movie_list = movies['title'].values
        return render_template('index.html', movie_list=movie_list)

@app.route('/recommendations/<selected_movie>', methods=['GET'])
def show_recommendations(selected_movie):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    movies = pickle.load(open('movie_list.pkl', 'rb'))
    return render_template('recommendations.html', movie_list=movies['title'].values,
                           movie=selected_movie,
                           recommended_names=recommended_movie_names,
                           recommended_posters=recommended_movie_posters)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
