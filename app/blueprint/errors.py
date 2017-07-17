from flask import render_template, request, jsonify
from . import blueprint

@blueprint.app_errorhandler(403)
def forbidden(e):
    '''Checks the `Accept` request header, which Werkzeug decodes into
    `request.accept_mimetypes`
    '''
    if (request.accept_mimetypes.accept_json and 
            not request.accept_mimettpes.accept_html):
        response = jsonify({'error': 'forbidden'})
        response.status_code = 403
        return response
    return render_template('blueprint/403.html'), 403

@blueprint.app_errorhandler(404)
def page_not_found(e):
    if (request.accept_mimetypes.accept_json and 
            not request.accept_mimettpes.accept_html):
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('blueprint/404.html'), 404

@blueprint.app_errorhandler(500)
def internal_server_error(e):
    if (request.accept_mimetypes.accept_json and 
            not request.accept_mimettpes.accept_html):
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    return render_template('blueprint/500.html'), 500