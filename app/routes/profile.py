from flask import render_template, redirect, url_for, flash, session, request
from app import app, db
from app.models import User
from app.models import Comment

@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    comments = Comment.query.filter_by(user_id=user.id).order_by(Comment.timestamp.desc()).all()
    current_user = None
    if 'user_id' in session:
        current_user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user, comments=comments, current_user=current_user)

@app.route('/follow/<username>', methods=['POST'])
def follow(username):
    if 'user_id' not in session:
        flash("Takip işlemi yapmak için giriş yapmalısınız.", "warning")
        return redirect(url_for('login'))
    user_to_follow = User.query.filter_by(username=username).first_or_404()
    current_user = User.query.get(session['user_id'])
    if current_user.id == user_to_follow.id:
        flash("Kendinizi takip edemezsiniz.", "warning")
        return redirect(url_for('profile', username=username))
    current_user.follow(user_to_follow)
    db.session.commit()
    flash(f"{username} kullanıcısını takip ettiniz.", "success")
    return redirect(url_for('profile', username=username))

@app.route('/unfollow/<username>', methods=['POST'])
def unfollow(username):
    if 'user_id' not in session:
        flash("Takipten çıkma işlemi yapmak için giriş yapmalısınız.", "warning")
        return redirect(url_for('login'))
    user_to_unfollow = User.query.filter_by(username=username).first_or_404()
    current_user = User.query.get(session['user_id'])
    if current_user.id == user_to_unfollow.id:
        flash("Kendinizi takipten çıkaramazsınız.", "warning")
        return redirect(url_for('profile', username=username))
    current_user.unfollow(user_to_unfollow)
    db.session.commit()
    flash(f"{username} kullanıcısını takipten çıktınız.", "success")
    return redirect(url_for('profile', username=username))
