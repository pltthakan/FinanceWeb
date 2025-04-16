from flask import render_template, request, session, redirect, url_for, flash
from app import app, db
from app.models import Comment, CommentLike, User
import datetime

@app.route('/comments') # ana yorumdur
def comments_page():
    comments = Comment.query.filter_by(parent_id=None).order_by(Comment.timestamp.desc()).all()
    current_user = None
    if 'user_id' in session:
        current_user = User.query.get(session['user_id'])
    return render_template("comments.html", comments=comments, current_user=current_user)

@app.route('/add_comment', methods=['POST'])
def add_comment():
    if 'user_id' not in session:
        flash("Yorum yapabilmek için giriş yapmalısınız.", "warning")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    now = datetime.datetime.utcnow()
    if user.comment_ban_until and user.comment_ban_until > now:
        flash("Yorum yapma yetkiniz geçici olarak kısıtlanmıştır. Lütfen daha sonra tekrar deneyin.", "warning")
        return redirect(url_for('comments_page'))

    comment_text = request.form.get('comment')
    parent_id = request.form.get('parent_id')
    if parent_id:
        try:
            parent_id = int(parent_id)
        except ValueError:
            parent_id = None
    else:
        parent_id = None

    if comment_text:
        new_comment = Comment(content=comment_text,
                              user_id=session['user_id'],
                              parent_id=parent_id)
        db.session.add(new_comment)
        db.session.commit()
        flash("Yorum eklendi.", "success")
    else:
        flash("Yorum boş olamaz.", "warning")
    return redirect(url_for('comments_page'))

@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    if 'user_id' not in session:
        flash("Yorum silebilmek için giriş yapmalısınız.", "warning")
        return redirect(url_for('login'))
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != session['user_id']:
        flash("Bu yorumu silemezsiniz.", "danger")
        return redirect(url_for('comments_page'))
    db.session.delete(comment)
    db.session.commit()
    flash("Yorum silindi.", "success")
    return redirect(url_for('comments_page'))

@app.route('/like_comment/<int:comment_id>', methods=['POST'])
def like_comment(comment_id):
    if 'user_id' not in session:
        flash("Yorum beğenmek için giriş yapmalısınız.", "warning")
        return redirect(url_for('login'))
    user_id = session['user_id']
    existing = CommentLike.query.filter_by(user_id=user_id, comment_id=comment_id).first()
    if existing:
        if existing.is_like:
            db.session.delete(existing)
        else:
            existing.is_like = True
    else:
        like = CommentLike(user_id=user_id, comment_id=comment_id, is_like=True)
        db.session.add(like)
    db.session.commit()
    return redirect(url_for('comments_page'))

@app.route('/dislike_comment/<int:comment_id>', methods=['POST'])
def dislike_comment(comment_id):
    if 'user_id' not in session:
        flash("Yorum beğenmemek için giriş yapmalısınız.", "warning")
        return redirect(url_for('login'))
    user_id = session['user_id']
    existing = CommentLike.query.filter_by(user_id=user_id, comment_id=comment_id).first()
    if existing:
        if not existing.is_like:
            db.session.delete(existing)
        else:
            existing.is_like = False
    else:
        dislike = CommentLike(user_id=user_id, comment_id=comment_id, is_like=False)
        db.session.add(dislike)
    db.session.commit()
    return redirect(url_for('comments_page'))
