#!/usr/bin/env python

from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return "Hello Voxxed people!", 200

@app.route('/name/<name>')
@app.route('/name/')
def custom_hello(name=None):
    if name is None:
        return "Tell me your name", 200
    else:
        return "Welcome to voxxed day " + name + "!", 200

# We only need this for local development.
if __name__ == '__main__':
    app.run()