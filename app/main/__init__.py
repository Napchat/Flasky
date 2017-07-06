from flask import Blueprint

main = Blueprint('main', __name__)

from . import views
from .. models import Permission

@main.app_context_processor
def inject_permission():
    '''Permissions may also need to be checked from templates, so the `Permission` class
    with all the bit constants needs to be accessible to them. To avoid having to add a 
    template argument in every `render_template` call, a `context processor` can be used.
    Context processors make variables globally available to all templates.
    '''
    return dict(Permission=Permission)