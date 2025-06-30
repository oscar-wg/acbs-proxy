import os
import flask
from flask_cors import CORS
import requests
from dotenv_vault import load_dotenv

load_dotenv()

proxy_target = os.getenv('PROXY_TARGET')
proxy_allow_origin = os.getenv('PROXY_ALLOW_ORIGIN')
method_requests_mapping = {
    'GET': requests.get,
    'HEAD': requests.head,
    'POST': requests.post,
    'PUT': requests.put,
    'DELETE': requests.delete,
    'PATCH': requests.patch,
    'OPTIONS': requests.options,
}

app = flask.Flask(__name__)
CORS(app, origins=proxy_allow_origin, allow_headers='*')

@app.route('/<path:url>', methods=method_requests_mapping.keys())
def proxy(url):
    if not(url[:7] == 'before/' or url[:4] == 'app/'):
        return flask.make_response('Path not found.', 404)
    requests_function = method_requests_mapping[flask.request.method]
    data = None
    headers = {
        'Content-Type': flask.request.headers['Content-Type'] if 'Content-Type' in flask.request.headers else 'application/x-www-form-urlencoded'
    }
    if flask.request.method in ['POST', 'PUT']:
        data=flask.request.form.to_dict() if 'form' in flask.request.headers['Content-Type'] else flask.request.data
    if 'X-Access-Token' in flask.request.headers:
        headers['X-Access-Token'] = flask.request.headers['X-Access-Token']
    request = requests_function(proxy_target + url, stream=True, headers=headers, params=flask.request.args, data=data)
    resp = flask.stream_with_context(request.iter_content())
    response =  flask.make_response(resp, request.status_code)
    response.headers['Content-Type'] = 'application/json'
    return response
