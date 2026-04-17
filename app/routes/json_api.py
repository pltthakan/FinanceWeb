# -----------------------------------------------------------------------------
# flask_json_patch.py
#
# SPA (React ön yüzü) için gereken iki küçük JSON endpoint'i ekler.
# Mevcut HTML endpoint'lerine dokunmaz; yan yana çalışır.
#
# KURULUM:
#   1. Bu dosyayı app/routes/ altına kopyala:  app/routes/json_api.py
#   2. app/__init__.py içine tek satır ekle:
#         from app.routes import main, auth, comments, profile, json_api
#   3. Flask sunucusunu yeniden başlat.
# -----------------------------------------------------------------------------

from flask import jsonify, session
from app import app
from app.models import User, Comment


def _serialize_comment(c, include_replies=True):
    data = {
        "id": c.id,
        "author": c.author.username if c.author else "?",
        "content": c.content,
        "timestamp": c.timestamp.isoformat() + "Z",
        "like_count": c.like_count,
        "dislike_count": c.dislike_count,
        "user_id": c.user_id,
        "parent_id": c.parent_id,
    }
    if include_replies:
        replies = (
            c.replies.order_by(Comment.timestamp.asc()).all()
            if hasattr(c.replies, "order_by") else list(c.replies)
        )
        data["replies"] = [_serialize_comment(r, include_replies=False) for r in replies]
    else:
        data["replies"] = []
    return data


@app.route("/api/comments")
def api_comments():
    """Top-level yorumlar + alt yorumları tek bir ağaç olarak döner."""
    roots = (
        Comment.query
        .filter_by(parent_id=None)
        .order_by(Comment.timestamp.desc())
        .all()
    )
    return jsonify([_serialize_comment(c) for c in roots])


@app.route("/api/profile/<username>")
def api_profile(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "Kullanıcı bulunamadı."}), 404

    comments = (
        Comment.query
        .filter_by(user_id=user.id)
        .order_by(Comment.timestamp.desc())
        .all()
    )

    current_user_id = session.get("user_id")
    is_followed = False
    if current_user_id:
        current = User.query.get(current_user_id)
        if current:
            is_followed = current.is_following(user)

    return jsonify({
        "username": user.username,
        "profile_image": getattr(user, "profile_image", None),
        "followers": [u.username for u in user.followers.all()],
        "following": [u.username for u in user.followed.all()],
        "comments": [_serialize_comment(c, include_replies=False) for c in comments],
        "is_followed_by_current": is_followed,
    })


@app.route("/api/me")
def api_me():
    """Oturum durumu — sayfa yenilemede React'ın kimin girişli olduğunu bilmesi için."""
    uid = session.get("user_id")
    if not uid:
        return jsonify({"user": None})
    user = User.query.get(uid)
    if not user:
        return jsonify({"user": None})
    return jsonify({"user": {
        "id": user.id,
        "username": user.username,
        "is_admin": getattr(user, "is_admin", False),
    }})
