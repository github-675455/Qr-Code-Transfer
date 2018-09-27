from flask import Flask, session, request, render_template, Response
from flask_socketio import SocketIO, emit
import os, secrets, qrcode, qrcode.image.svg
import io
import logging, sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger()

app = Flask(__name__)

secret_session_key = os.environ.get('secret_key')

if secret_session_key == None:
    app.secret_key = 'default'
else:
    app.secret_key = secret_session_key

socketio = SocketIO(app)

clients = {}

@app.route('/generate-qr-code')
def create_pipeline():

    local_session = request.cookies.get('session')

    qrcode_generated = qrcode.make(local_session, image_factory=qrcode.image.svg.SvgFillImage)

    byteStream = io.BytesIO()

    qrcode_generated.save(stream=byteStream)

    return Response(byteStream.getvalue().decode(encoding="ascii", errors="ignore"), mimetype='image/svg+xml')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan')
def scan():
    return render_template('scan.html')

@socketio.on('join')
def join_pipeline(data):
    log.info(' join channel with id: ' + request.sid)
    log.info(' data: ' + data['sessionid'])
    log.info(' ip: ' + request.remote_addr)


@socketio.on('global')
def global_pipeline(data):
    print("%s connected" % (request.namespace.socket.sessid))
    log.info(' join global pipiline socket ip: ' + request.remote_addr)

@socketio.on('connect')
def connected():
    s = request.cookies.get('session')

    if clients.get(s) is None:
        clients[s] = [request.sid]
    else:
        clients[s].append(request.sid)

    print("%s connect" % (request.sid))

@socketio.on('ping')
def connected():
    print("%s ping" % (request.sid))

@socketio.on('message')
def message(data):
    pipeline_selecionado = data['user']

    clientes_pipeline = clients.get(pipeline_selecionado)

    for cliente in clientes_pipeline:
        if cliente == request.sid:
            continue

        emit('message', data['message'], room=cliente)


@socketio.on('disconnect')
def disconnect():
    print("%s disconnected" % (request.sid))
    s = request.cookies.get('session')
    if not clients.get(s) is None:
        clients[s].remove(request.sid)
        if len(clients[s]) == 0:
            clients[s] = None



@app.before_request
def create_session():
    session_id = session.get('id')

    if session_id == None:
        session_id = secrets.token_hex(32)
        session['id'] = session_id


if __name__ == '__main__':
    app.run()

