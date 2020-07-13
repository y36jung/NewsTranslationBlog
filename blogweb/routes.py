import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from blogweb import app, db, bcrypt
from blogweb.forms import SignupForm, LoginForm, PostForm, CommentForm, UpdateAccountForm, SearchForm
from blogweb.models import User, Posting, Comments
from flask_login import login_user, current_user, logout_user, login_required

session = {'url':[]}

@app.route('/', methods=['POST', 'GET'])
@app.route('/home', methods=['POST', 'GET'])
def home():
    page = request.args.get('page', 1, type=int)
    all_posts = Posting.query.all()
    page_posts = Posting.query.order_by(Posting.date_published.desc()).paginate(page=page, per_page=5)
    form = SearchForm()
    if request.method == 'POST':
        for post in all_posts:
            if form.search_title.data == post.title:
                results = Posting.query.filter_by(title=post.title).paginate(page=page, per_page=5)
                return render_template('search_results.html', posts=results, form=form)
        else:
            flash('No results found!')
            return render_template('home.html', posts=page_posts, form=form)
    else:
        return render_template('home.html', posts=page_posts, form=form)

@app.route('/post/new', methods=['POST', 'GET'])
def newpost():
    form = PostForm()
    if form.validate_on_submit():
        post_title = request.form['title']
        post_content = request.form['content']
        new_post = Posting(title=post_title, author=current_user, content=post_content)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/')
    else:
        return render_template('newpost.html', title='New Post', form=form)

@app.route('/post/<int:id>', methods=['POST', 'GET'])
def post(id):
    all_comments = Comments.query.all()
    comments = []
    for comment in all_comments:
        if comment.post_id == id:
            comments.append(comment)

    post = Posting.query.get_or_404(id)
    form = CommentForm()

    if form.validate_on_submit():
        com_content = request.form['content']
        new_comment = Comments(author=current_user, content=com_content, post_id=id)
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('post', id=id))
    else:
        session['url'] = url_for('post', id=id)
        return render_template('post.html', post=post, comments=comments, form=form)

@app.route('/post/<int:id>/delete')
def delete(id):
    post = Posting.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/')

@app.route('/post/<int:id>/edit', methods=['POST', 'GET'])
def edit(id):
    post = Posting.query.get_or_404(id)
    form = PostForm()

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        return redirect('/post/' + str(id))
    else:
        return render_template('edit.html', post=post, form=form)

@app.route('/comment/<int:id>/delete')
def cdelete(id):
    comment = Comments.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    if 'url' in session:
        return redirect(session['url'])
    else:
        return redirect('/')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! You are now able to log in!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', title='Signup', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route('/profile/<int:id>', )
@login_required
def profile(id):
    user = User.query.get_or_404(id)
    form = UpdateAccountForm()
    form.username.data = user.username
    form.email.data = user.email
    form.about.data = user.about
    image = url_for('static', filename='profile_pics/' + user.image)
    return render_template('profile.html', title='Profile', image=image, form=form, user=user)

@app.route('/profile/update', methods=['POST', 'GET'])
@login_required
def updateprofile():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.about = form.about.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('profile', id=current_user.id))
    else:
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.about.data = current_user.about
    image = url_for('static', filename='profile_pics/' + current_user.image)
    return render_template('updateprofile.html', title='Update Profile', image=image, form=form)