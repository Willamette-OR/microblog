from datetime import datetime
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required


from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm
from app.models import User, Post


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    """View function for the index page"""

    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().\
        paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None

    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()

        flash('You have successfully submitted a new post!')
        return redirect(url_for('index'))

    return render_template('index.html', title='Home', user=current_user,
                           posts=posts.items, form=form, next_url=next_url,
                           prev_url=prev_url)


@app.route('/explore')
@login_required
def explore():
    """View function to allow logged in users to explore all user posts"""

    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).\
        paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) if posts.has_next \
        else None
    prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev \
        else None

    return render_template('index.html', title='Explore', user=current_user,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """View function for the login page"""

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is not None and user.check_password(form.password.data):
            login_user(user)
            flash('You have logged in successfully!')
            return redirect(url_for('index'))

        flash('Invalid username or password. Please try again.')
        return redirect(url_for('login'))

    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    """View function for user logout"""

    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """View function to register new users"""

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('You have registered successfully! Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html', form=form, title='Register')


@app.route('/user_profile/<username>')
@login_required
def user_profile(username):
    """View function to display user profiles"""

    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User {} does not exist.'.format(username))
        return redirect(url_for('index'))

    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).\
        paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user_profile', username=user.username,
                       page=posts.next_num) if posts.has_next else None
    prev_url = url_for('user_profile', username=user.username,
                       page=posts.prev_num) if posts.has_prev else None

    return render_template('user_profile.html', user=user, title='Profile',
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """View function to edit user profiles"""

    form = EditProfileForm(current_user)

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()

        flash('Your profile has been updated successfully!')
        return redirect(url_for('user_profile', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', form=form, title='Edit Profile')


@app.route('/follow/<username>')
@login_required
def follow(username):
    """View function to handle requests to follow a different user"""

    if username == current_user.username:
        flash('You cannot follow yourself!')
        return redirect(url_for('index'))

    user = User.query.filter_by(username=username).first()
    current_user.follow(user)
    db.session.commit()
    flash('You are now following {}!'.format(username))
    return redirect(url_for('user_profile', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    """View function to handle requests to unfollow a different user"""

    if username == current_user.username:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('index'))

    user = User.query.filter_by(username=username).first()
    current_user.unfollow(user)
    db.session.commit()
    flash('You are no longer following {}!'.format(username))
    return redirect(url_for('user_profile', username=username))


@app.before_request
def before_request():
    """Actions to take before each request"""

    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
