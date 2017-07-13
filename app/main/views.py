from flask import render_template, redirect, flash, url_for, request, current_app
from flask_login import login_required, current_user

from . import main
from ..models import User, db, Role, Permission, Post, Follow, Comment
from ..decorators import permission_required, admin_required
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm

@main.route('/', methods=['GET', 'POST'])
@main.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if (current_user.can(Permission.WRITE_ARTICLES) and 
            form.validate_on_submit()):
        # `current_user` is a LocalProxy() instance, it is readlly a thin
        # wrapper that contains the actual user object inside. If you want to 
        # get the real user object, you need to call `_get_current_object()`
        post = Post(body=form.body.data, 
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.index'))

    # The page number to render is obrained from the request's query string, which
    # is available as `request.args`. When an explicit page isn't given, a default
    # page of 1(the first page) is used. The `type=int` argument ensures that if the 
    # argument cannot be converted to an integer, the default value is returned.
    page = request.args.get('page', 1, type=int)
    pagination = (current_user.followed_posts.order_by(Post.timestamp.desc()).
        paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], 
                 error_out=False))
    posts = pagination.items
    return render_template('main/index.html', form=form, 
                           posts=posts, pagination=pagination)

@main.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User %s is not found.' % username)
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = (Post.query.filter_by(author=user).order_by(Post.timestamp.desc()).
        paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], 
                 error_out=False))
    posts = pagination.items
    return render_template('main/user.html', user=user, 
                            posts=posts, pagination=pagination)

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('main/edit_profile.html', form=form)

@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('main.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_name
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('main/edit_profile.html', form=form, user=user)

@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('The post has been updated')
        return redirect(url_for('main.post', id=post.id))
    form.body.data = post.body
    return render_template('main/edit_post.html', form=form)

@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    if current_user.can(Permission.COMMENT):
        form = CommentForm()
        if form.validate_on_submit():
                comment = Comment(body=form.body.data, post=post, 
                    author=current_user._get_current_object())
                db.session.add(comment)
                db.session.commit()
                return redirect(url_for('main.post', id=post.id))
    page = request.args.get('page', 1, type=int)
    '''if page == -1:
        page = (post.comments.count() - 1) / current_app \
            .config['FLASKY_COMMENTS_PER_PAGE']'''
    pagination = post.comments.order_by(Comment.timestamp.desc()).paginate(page, 
        per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    return render_template('main/post.html', posts=[post], 
        form=form, comments=comments, pagination=pagination)

@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Not found user %s' % username)
        return redirect(url_for('main.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    flash('You are now following %s.' % username)
    return redirect(url_for('main.user', username=username))

@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Not found user %s' % username)
        return redirect(url_for('main.index'))
    if not current_user.is_following(user):
        flash('You are not following %s.' % username)
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    flash('You have unfollowed %s.' % username)
    return redirect(url_for('main.user', username=username))

@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Not found user %s' % username)
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.order_by(Follow.timestamp.desc()).paginate( \
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'], error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
                 for item in pagination.items]
    return render_template('main/followers.html', follows=follows, user=user,
                           endpoint='main.followers', pagination=pagination, 
                           title='Followers of')

@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Not found user %s' % username)
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.order_by(Follow.timestamp.desc()).paginate(page, 
        per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'], error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
                 for item in pagination.items]
    return render_template('main/followers.html', follows=follows, user=user,
                           endpoint='main.followed_by', pagination=pagination, 
                           title='Followed by')

@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('main/moderate.html', comments=comments,
                           pagination=pagination, page=page)

@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('main.moderate', 
                            page=request.args.get('get', 1, type=int)))

@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('main.moderate',
                            page=request.args.get('page', 1, type=int)))