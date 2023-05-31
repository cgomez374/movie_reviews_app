from main import app, render_template, url_for, redirect, request
import requests

# Movies endpoint
API_KEY = '2981946d7a75ea943692c98fb27ce426'

popular_movies_endpoint = f'https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=en-US&page=1'
latest_movies_endpoint = f'https://api.themoviedb.org/3/movie/now_playing?api_key={API_KEY}&language=en-US&page=1'


@app.route('/')
def main():
    popular_movies_response = requests.get(popular_movies_endpoint)
    latest_movies_response = requests.get(latest_movies_endpoint)
    if popular_movies_response.status_code == 200 and latest_movies_response.status_code == 200:
        popular_movies = [popular_movies_response.json()['results'][i]
                          for i in range(0, len(popular_movies_response.json()['results']))
                          if i < 10]
        latest_movies = [latest_movies_response.json()['results'][i]
                         for i in range(0, len(latest_movies_response.json()['results']))
                         if i < 10]
    else:
        print(f'Popular query status code: ', popular_movies_response.status_code)
        print(f'Latest query status code: ', latest_movies_response.status_code)
    return render_template('index.html', popular_movies=popular_movies, latest_movies=latest_movies)


@app.route('/movie/<int:movie_id>')
def show_movie(movie_id):
    movie_details_endpoint = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}'
    response = requests.get(movie_details_endpoint)
    if response.status_code == 200:
        movie = response.json()
    return render_template('show_movie.html', movie=movie)


@app.route('/search', methods=['GET', 'POST'])
def search_movie():
    if request.method == 'POST' and request.form:
        movie_title = request.form['title'].lower()
        search_movie_endpoint = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&language=en-US&query="
        response = requests.get(search_movie_endpoint + movie_title)
        if response.status_code == 200:
            results = response.json()['results']
            return render_template('search.html', movies=results)
        else:
            print(response.status_code)
    return render_template('search.html', movies=[])


@app.route('/browse/<int:current_page>')
def browse_all_movies(current_page):
    endpoint = f'https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}' \
               f'&include_adult=false&include_video=false&language=en-US&page={current_page}' \
               f'&region=us&primary_release_year=2023&sort_by=primary_release_date.desc'
    response = requests.get(endpoint)
    if response.status_code == 200:
        # print(len(response.json()['results']))
        movies = response.json()['results']
    else:
        print(response.status_code)
    return render_template('browse.html', movies=movies, current_page=current_page)
