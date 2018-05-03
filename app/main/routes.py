from datetime import datetime
from guess_language import guess_language
import os
from flask import render_template, redirect, url_for, flash, request, g, \
    jsonify, current_app, send_from_directory
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from werkzeug.utils import secure_filename


from app import db
from app.models import User, Post
from app.translate import translation
from app.main import bp
from app.main.forms import EditProfileForm, PostForm, SearchForm, PhotoForm
from app.uploads import filename_hash


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    """View function for the index page"""

    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().\
        paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None

    form = PostForm()
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language in ['UNKNOWN', 'la'] or len(language) > 5:
            language = ''
        post = Post(body=form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()

        flash(_('You have successfully submitted a new post!'))
        return redirect(url_for('main.index'))

    return render_template('index.html', title=_('Home'), user=current_user,
                           posts=posts.items, form=form, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/explore')
@login_required
def explore():
    """View function to allow logged in users to explore all user posts"""

    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).\
        paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) if posts.has_next \
        else None
    prev_url = url_for('main.explore', page=posts.prev_num) if posts.has_prev \
        else None

    return render_template('index.html', title='Explore', user=current_user,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/user_profile/<username>')
@login_required
def user_profile(username):
    """View function to display user profiles"""

    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User {} does not exist.'.format(username))
        return redirect(url_for('main.index'))

    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).\
        paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user_profile', username=user.username,
                       page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user_profile', username=user.username,
                       page=posts.prev_num) if posts.has_prev else None

    return render_template('user_profile.html', user=user, title='Profile',
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """View function to edit user profiles"""

    form = EditProfileForm(current_user)

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()

        flash('Your profile has been updated successfully!')
        return redirect(url_for('main.user_profile',
                                username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', form=form, title='Edit Profile')


@bp.route('/upload_profile_pic', methods=['GET', 'POST'])
@login_required
def upload_profile_pic():
    """View function to upload profile pictures"""

    form = PhotoForm()
    # TODO - refresh the image on the client side only when uploading new images
    if form.validate_on_submit():
        file = form.upload.data
        filename = filename_hash(secure_filename(file.filename),
                                 current_user.email)
        file.save(os.path.join(current_app.config['UPLOADS_URL'], filename))
        current_user.photo_name = filename
        db.session.commit()
        flash('Your profile photo has been updated!')
        return redirect(url_for('main.user_profile',
                                username=current_user.username))
    return render_template('photo_upload.html', form=form)


@bp.route('/profile_photos/<filename>')
@login_required
def profile_photos(filename):
    """View function to serve uploaded profile photos"""

    return send_from_directory(current_app.config['UPLOADS_URL'], filename)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    """View function to handle requests to follow a different user"""

    if username == current_user.username:
        flash('You cannot follow yourself!')
        return redirect(url_for('main.index'))

    user = User.query.filter_by(username=username).first()
    current_user.follow(user)
    db.session.commit()
    flash('You are now following {}!'.format(username))
    return redirect(url_for('main.user_profile', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    """View function to handle requests to unfollow a different user"""

    if username == current_user.username:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('main.index'))

    user = User.query.filter_by(username=username).first()
    current_user.unfollow(user)
    db.session.commit()
    flash('You are no longer following {}!'.format(username))
    return redirect(url_for('main.user_profile', username=username))


@bp.route('/translate', methods=['POST'])
@login_required
def translate():
    """Post-only view function to translate texts and return translated texts
    in json"""

    return jsonify({'text': translation(request.form['text'],
                                        request.form['source_lang'],
                                        request.form['dest_lang'])})


@bp.route('/search')
@login_required
def search():
    """View function to handle search requests"""

    if not g.search_form.validate():
        return redirect(url_for('main.explore'))

    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])

    next_url = url_for('main.search', q=g.search_form.q.data, page=(page + 1)) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=(page - 1)) \
        if (page - 1) > 0 else None
    return render_template('index.html', title='Search Results', posts=posts,
                           next_url=next_url, prev_url=prev_url,
                           user=current_user, search_results=True)


@bp.before_app_request
def before_request():
    """Actions to take before each request"""

    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()

    # Register flask babel locale with flask g?
    g.locale = str(get_locale())
