from wsgiref.handlers import CGIHandler
from abbvie_web_app import app

CGIHandler().run(app)