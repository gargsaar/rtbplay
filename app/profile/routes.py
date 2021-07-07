from flask import render_template, Blueprint, current_app
from flask_login import login_required, current_user

profile = Blueprint('profile', __name__)


# profile
@profile.route("/profile", methods=["GET", "POST"])
@login_required
def user_profile():
    return render_template("/public/profile-page/page-wip.html",
                           user=current_user,
                           title='RTB | Brainy Fun',
                           segment_key=current_app.config['SEGMENT_JS_TRACKING_KEY'],
                           ga_site_tag=current_app.config['GA_SITE_TAG'])
