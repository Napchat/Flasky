from flask import Flask

def create_app(config):
    app = Flask(__name__)

    from blueprint import blueprint
    app.register_blueprint(blueprint)

    return app