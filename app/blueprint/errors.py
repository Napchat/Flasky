from flask import render_template
from . import blueprint

@blueprint.app_errorhandler(403)
def forbidden(e):
    return render_template('blueprint/403.html'), 403

@blueprint.app_errorhandler(404)
def page_not_found(e):
    return render_template('blueprint/404.html'), 404

@blueprint.app_errorhandler(500)
def internal_server_error(e):
    return render_template('blueprint/500.html'), 500