
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from models import User

login_manager = LoginManager()

login_manager.login_view = "login"
# We have not created the users.login view yet
# but that is the name that we will use for our
# login view, so we will set it now.


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)