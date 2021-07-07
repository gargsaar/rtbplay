from flask import Blueprint, render_template, current_app

handlers = Blueprint('handlers', __name__)


@handlers.app_errorhandler(404)
def error_404(error):
    return render_template('/public/error-page/page-404.html',
                           segment_key=current_app.config['SEGMENT_JS_TRACKING_KEY'],
                           ga_site_tag=current_app.config['GA_SITE_TAG']), 404


@handlers.app_errorhandler(403)
def error_403(error):
    return render_template('/public/error-page/page-403.html',
                           segment_key=current_app.config['SEGMENT_JS_TRACKING_KEY'],
                           ga_site_tag=current_app.config['GA_SITE_TAG']), 403


@handlers.app_errorhandler(500)
def error_500(error):
    return render_template('/public/error-page/page-500.html',
                           segment_key=current_app.config['SEGMENT_JS_TRACKING_KEY'],
                           ga_site_tag=current_app.config['GA_SITE_TAG']), 500
