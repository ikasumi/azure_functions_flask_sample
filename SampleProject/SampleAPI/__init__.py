import logging
import azure.functions as func
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/hi')
def hi():
    return 'Hi World!'

@app.route('/hello')
@app.route('/hello/<name>', methods=['POST', 'GET'])
def hello(name=None):
    return name != None and 'Hello, '+name or 'Hello, '+request.args.get('name')

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    uri=req.params['uri']
    with app.test_client() as c:
        doAction = {
            "GET": c.get(uri).data,
            "POST": c.post(uri).data
        }
        resp = doAction.get(req.method).decode()
        return func.HttpResponse(resp, mimetype='text/html')