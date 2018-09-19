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

clients = []

@app.route('/generate-qr-code')
def create_pipeline():

    log.info('session_id: ' + session['id'])

    qrcode_generated = qrcode.make(session['id'], image_factory=qrcode.image.svg.SvgFillImage)

    byteStream = io.BytesIO()

    qrcode_generated.save(stream=byteStream)

    return Response(byteStream.getvalue().decode(encoding="ascii", errors="ignore"), mimetype='image/svg+xml')

@app.before_request
def create_session():
    session_id = session.get('id')

    if session_id == None:
        session_id = secrets.token_hex(5)
        session['id'] = session_id


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

@socketio.on('connected')
def connected():
    print("%s connected" % (request.sid))
    clients.append(request.sid)

@socketio.on('message')
def message(data):
    emit('message', data['message'], room=data['usuario'])

@socketio.on('disconnect')
def disconnect():
    print("%s disconnected" % (request.sid))
    clients.remove(request.sid)


if __name__ == '__main__':
    app.run()

