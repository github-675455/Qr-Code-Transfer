from flask import Flask, session, request, render_template, Response
from flask_socketio import SocketIO
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

@app.route('/generate-qr-code')
def create_pipeline():
    session_id = session.get('id')

    if session_id == None:
        session_id = secrets.token_hex(256)
        session['id'] = session_id

    log.info('session_id: ' + session_id)

    qrcode_generated = qrcode.make(session_id, image_factory=qrcode.image.svg.SvgFillImage)

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
def join_pipeline():
    log.info(' join socket ip: ' + request.remote_addr)



if __name__ == '__main__':
    app.run()

