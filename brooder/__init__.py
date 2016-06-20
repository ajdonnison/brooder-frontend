# -*- coding: utf-8 -*-
from flask import Flask, session, g, render_template
import sys
sys.path.append('/home/pi')

app = Flask(__name__)
app.config.from_object('siteconfig')
app.secret_key = ']\xf8\xaf\xc4f\x101a\xe2<\x96\x84\xcd\xf1\x01T\xe9\xda\x97s\xc5,\x06&'

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

from brooder.views import brooder
app.register_blueprint(brooder.mod)
