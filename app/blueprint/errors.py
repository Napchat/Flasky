from flask import render_template, request, jsonify
from . import blueprint

'''The handling of status codes 404 and 500 presents a small complication,
in that these errors are generated by Flask on its own and will ususally
return an HTML response, which is likely to confuse an API client. 
    we need to make the error handlers adapt their response based on the 
requested by the client.
'''

@blueprint.app_errorhandler(404)
def page_not_found(e):
    if (request.accept_mimetypes.accept_json and 
            not request.accept_mimetypes.accept_html):
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('blueprint/404.html'), 404

@blueprint.app_errorhandler(500)
def internal_server_error(e):
    if (request.accept_mimetypes.accept_json and 
            not request.accept_mimetypes.accept_html):
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    return render_template('blueprint/500.html'), 500