"""
# coding:utf-8
@Time    : 2020/12/09
@Author  : jiangwei
@mail    : jiangwei1@kylinos.cn
@File    : profile.py
@Software: PyCharm
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required

from bbs.models import User, Comments, Post, Collect
from bbs.blueprint.post import post_collect

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')


@profile_bp.route('/user/<user_id>/')
def index(user_id):
    page = request.args.get('page', default=1, type=int)
    user = User.query.get_or_404(user_id)
    # 其他人查看用户信息时候屏蔽用户匿名发表的帖子
    if current_user.id == int(user_id):
        pagination = Post.query.filter(Post.author_id == user_id, Post.status_id == 1).order_by(
            Post.create_time.desc()).paginate(page=page, per_page=20)
        posts = pagination.items
    else:
        pagination = Post.query.filter(Post.author_id == user_id, Post.status_id == 1, Post.is_anonymous == 1).order_by(
            Post.create_time.desc()).paginate(page=page, per_page=20)
        posts = pagination.items
    return render_template('frontend/profile.html', user=user, pagination=pagination, posts=posts)


@profile_bp.route('/comment/<user_id>/')
def profile_comment(user_id):
    page = request.args.get('page', default=1, type=int)
    user = User.query.get_or_404(user_id)
    pagination = Comments.query.filter(Comments.author_id == user.id, Comments.delete_flag == 0).order_by(
        Comments.timestamps.desc()).paginate(page=page, per_page=20)
    comments = pagination.items
    return render_template('frontend/profile-comment.html', user=user, comments=comments)


current_user: User


@profile_bp.route('/follow/<user_id>/')
@login_required
def follow_user(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.is_following(user):
        flash('你已经关注TA了!', 'info')
        return redirect(url_for('.index', user_id=user_id))
    current_user.follow(user)
    flash('关注成功!', 'success')
    return redirect(url_for('.index', user_id=user_id))


@profile_bp.route('/unfollow/<user_id>/')
@login_required
def unfollow_user(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.is_following(user):
        current_user.unfollow(user)
        flash('取关成功!', 'success')
        return redirect(url_for('.index', user_id=user_id))


@profile_bp.route('/collect/<user_id>/')
@login_required
def collect(user_id):
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', default=1, type=int)
    pagination = Collect.query.with_parent(user).order_by(Collect.timestamps.desc()).paginate(page=page, per_page=20)
    collects = pagination.items
    print(collects)
    return render_template('frontend/profile-collections.html', user=user, pagination=pagination, collects=collects)


@profile_bp.route('/uncollect/<post_id>')
def uncollect(post_id):
    post_collect(post_id)
    return redirect(url_for('.collect', user_id=current_user.id))