import datetime
from flask import session, redirect, url_for, flash
from flask_admin import AdminIndexView
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

#########################################
# VERİTABANI MODELLERİ: User, Comment, CommentLike
#########################################

# Takip (followers) ilişkisi için yardımcı tablo (Many-to-Many)
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        # Sadece giriş yapmış ve admin yetkisine sahip kullanıcılar erişsin.
        return session.get("user_id") and session.get("is_admin", False)

    def inaccessible_callback(self, name, **kwargs):
        flash("Admin paneline erişim izniniz yok.", "danger")
        return redirect(url_for("login"))

from flask_admin.contrib.sqla import ModelView

class AdminModelView(ModelView):
    def is_accessible(self):
        # Mevcut kullanıcı adminse erişime izin ver.
        return session.get("user_id") and session.get("is_admin", False)

    def inaccessible_callback(self, name, **kwargs):
        flash("Admin paneline erişim izniniz yok.", "danger")
        return redirect(url_for("login"))

class CustomUserAdmin(AdminModelView):
    form_args = {
        'comment_ban_until': {
            'format': '%Y-%m-%d %H:%M:%S'  # Tarih formatını zorunlu kıl
        }
    }
    column_list = ('id', 'username', 'email', 'is_admin', 'comment_ban_until')
    form_columns = ('username', 'email', 'is_admin', 'comment_ban_until')

class User(db.Model):
    __table_args__ = (
        db.Index('idx_user_username', 'username'),
        db.Index('idx_user_email', 'email'),
    )
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    profile_image = db.Column(db.String(200), nullable=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    is_admin = db.Column(db.Boolean, default=False)  # Yönetici yetkisi için alan
    comment_ban_until = db.Column(db.DateTime, nullable=True)  # Yorum yapma yasağı bitiş zamanı

    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

class Comment(db.Model):
    __table_args__ = (
        db.Index('idx_comment_user_id', 'user_id'),
        db.Index('idx_comment_timestamp', 'timestamp'),
    )
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    replies = db.relationship('Comment',
                              backref=db.backref('parent', remote_side=[id]),
                              cascade="all, delete-orphan",
                              lazy='dynamic')

    @property
    def like_count(self):
        from app.models import CommentLike  # Circular import engellemek için yerel import
        return CommentLike.query.filter_by(comment_id=self.id, is_like=True).count()

    @property
    def dislike_count(self):
        from app.models import CommentLike
        return CommentLike.query.filter_by(comment_id=self.id, is_like=False).count()

class CommentLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=False)
    is_like = db.Column(db.Boolean, nullable=False)  # True: Like, False: Dislike
    __table_args__ = (db.UniqueConstraint('user_id', 'comment_id', name='_user_comment_uc'),)

# Bu satır, jinja ortamına Comment sınıfını ekler.
from app import app
app.jinja_env.globals['Comment'] = Comment
