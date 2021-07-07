from flask import render_template, Blueprint, flash, redirect, url_for, current_app
from app.general.forms import ContactForm
from flask_login import login_required, current_user
from datetime import datetime
from app.general.utils import post_contact_to_db

general = Blueprint('general', __name__)


# about
@general.route("/about", methods=["GET", "POST"])
def about():
    return render_template("/public/general-page/about.html",
                           title='RTB | About',
                           segment_key=current_app.config['SEGMENT_JS_TRACKING_KEY'],
                           ga_site_tag=current_app.config['GA_SITE_TAG'])


# contact
@general.route('/contact', methods=["GET", "POST"])
@login_required
def contact():
    # get the contact form
    form = ContactForm()

    if form.validate_on_submit():
        flash(f'Message sent. Thank you for reaching out!', 'success')

        # post message to database
        post_contact_to_db(form.email.data, form.message.data)
        return redirect(url_for('main.index'))

    return render_template("/public/general-page/contact.html",
                           user=current_user,
                           today_date=datetime.now().strftime("%d-%B-%Y"),
                           form=form,
                           title='RTB | Contact',
                           segment_key=current_app.config['SEGMENT_JS_TRACKING_KEY'],
                           ga_site_tag=current_app.config['GA_SITE_TAG'])
