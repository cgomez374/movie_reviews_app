from main import app, render_template, url_for, redirect, request, flash, login_manager, login_user, LoginManager, \
    login_required, current_user, logout_user
from models import db, User, Review
import requests

# Movies endpoint
API_KEY = '2981946d7a75ea943692c98fb27ce426'

popular_movies_endpoint = f'https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=en-US&page=1'
latest_movies_endpoint = f'https://api.themoviedb.org/3/movie/now_playing?api_key={API_KEY}&language=en-US&page=1'


# Load the user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def main():
    # db.drop_all()
    # db.create_all()
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
    return render_template('index.html', popular_movies=popular_movies, latest_movies=latest_movies,
                           logged_in=current_user.is_authenticated)


@app.route('/movie/<int:movie_id>')
def show_movie(movie_id):
    movie_details_endpoint = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}'
    response = requests.get(movie_details_endpoint)
    if response.status_code == 200:
        # Get the movie details from API
        movie = response.json()

        # Get all reviews for this movie from DB
        all_reviews = Review.query.filter_by(movie_id=movie_id).all()

        # has the user left a review?
        has_reviewed = False
        current_user_review = None
        current_user_review_id = None

        # Get the review that the current user has written from DB if logged in
        if current_user.is_authenticated:
            current_user_review = Review.query.filter_by(author_id=current_user.id).filter_by(movie_id=movie_id).first()
            if current_user_review:
                has_reviewed = True
                current_user_review_id = current_user_review.id
        return render_template('show_movie.html',
                               movie=movie,
                               reviews=all_reviews,
                               logged_in=current_user.is_authenticated,
                               has_reviewed=has_reviewed,
                               current_user_review_id=current_user_review_id)
    return render_template('404_not_found.html')


@app.route('/search', methods=['GET', 'POST'])
def search_movie():
    if request.method == 'POST' and request.form:
        movie_title = request.form['title'].lower()
        search_movie_endpoint = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&language=en-US&query="
        response = requests.get(search_movie_endpoint + movie_title)
        if response.status_code == 200:
            results = response.json()['results']
            return render_template('search.html', movies=results, logged_in=current_user.is_authenticated)
        else:
            print(response.status_code)
    return render_template('search.html', movies=[], logged_in=current_user.is_authenticated)


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
    return render_template('browse.html', movies=movies, current_page=current_page,
                           logged_in=current_user.is_authenticated)


@app.route('/register', methods=['GET', 'POST'])
def register():
    # STILL NEED TO BUILD IN SOME VALIDATION FOR THE EMAIL; HTML NOT ENOUGH!!!!!

    if request.method == 'POST':
        # Build the user model
        new_user = User(
            name=request.form.get('first_name') + ' ' + request.form.get('last_name'),
            email=request.form.get('email')
        )
        # set the password
        new_user.set_password(request.form.get('password'))

        # add to db
        db.session.add(new_user)

        # commit db
        try:
            db.session.commit()
            flash('Account created successfully!')
        except:
            db.session.rollback()
            flash('Error in creating account! Please Try again!')
        return redirect(url_for('login'))
    return render_template('register.html', logged_in=current_user.is_authenticated)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form.get('email')).first()
        if not user or not user.check_password(request.form.get('password')):
            flash('incorrect email/password combination')
            return redirect(url_for('register'))
        # login user
        login_user(user)
        return redirect(url_for('main'))
    return render_template('login.html', logged_in=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main'))


# NEED TO DISABLE BACK BUTTON OR AT LEAST NOT ALLOW TO ADD THE SAME POST AGAIN!!!!

@app.route('/new-review/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def new_review(movie_id):
    current_user_review = Review.query.filter_by(author_id=current_user.id).filter_by(movie_id=movie_id).first()
    if current_user_review is None:
        movie_details_endpoint = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}'
        response = requests.get(movie_details_endpoint)
        movie = None
        if response.status_code == 200:
            movie = response.json()

        if request.method == 'POST':
            review = Review(
                content=request.form.get('content'),
                movie_name=movie['title'],
                movie_id=movie_id,
                author_id=int(current_user.id)
            )

            # add to db
            db.session.add(review)

            # commit changes
            try:
                db.session.commit()
                return redirect(url_for('show_movie', movie_id=movie_id, logged_in=current_user.is_authenticated))
            except:
                db.session.rollback()
    else:
        return redirect(url_for('show_movie', movie_id=movie_id, logged_in=current_user.is_authenticated))
    return render_template('new_review.html', movie_id=movie_id, logged_in=current_user.is_authenticated)


@app.route('/edit-review/<int:current_user_review_id>', methods=['GET', 'POST'])
@login_required
def edit_review(current_user_review_id):
    review = Review.query.get(current_user_review_id)
    if request.method == 'POST':
        review.content = request.form.get('content')
        # commit changes
        try:
            db.session.commit()
        except:
            db.session.rollback()
        return redirect(url_for('show_movie', movie_id=review.movie_id, logged_in=current_user.is_authenticated))
    return render_template('edit_review.html', current_user_review_id=current_user_review_id,
                           logged_in=current_user.is_authenticated)


@app.route('/delete-review/<int:current_user_review_id>', methods=['GET'])
@login_required
def delete_review(current_user_review_id):
    review_to_delete = Review.query.get(current_user_review_id)
    movie_id = review_to_delete.movie_id
    db.session.delete(review_to_delete)
    try:
        db.session.commit()
    except:
        db.session.rollback()
    return redirect(url_for('show_movie', movie_id=movie_id, logged_in=current_user.is_authenticated))


@app.route('/account')
@login_required
def user_account():
    for review in current_user.reviews:
        print(review.movie_name)
    return render_template("account.html", user=current_user, logged_in=current_user.is_authenticated)
