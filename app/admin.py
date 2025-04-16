from flask_admin import Admin
from app.models import MyAdminIndexView, AdminModelView, User, Comment, CommentLike
from app import app, db

admin = Admin(app, name="Admin Paneli", template_mode="bootstrap3", index_view=MyAdminIndexView())
admin.add_view(AdminModelView(User, db.session))
admin.add_view(AdminModelView(Comment, db.session))
admin.add_view(AdminModelView(CommentLike, db.session))
