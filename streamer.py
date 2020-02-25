# Web streaming example
#
# Super useful for initial camera setup, especially focusing.
#
# This is really just source code from the official PiCamera package,
#   so go check this out for more details and information:
#
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming


import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server
from fractions import Fraction

PAGE="""\
<html>
<head>
<title>The Great Printzini - Webcam</title>
</head>
<body bgcolor='black'>
<center><h1 style="color:white">The Great Printzini's Webcam</h1></center>
<center><img src="stream.mjpg" width="820" height="616"></center>
</body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
            self.frame = None
            self.buffer = io.BytesIO()
            self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
      if self.path == '/':
          self.send_response(301)
          self.send_header('Location', '/index.html')
          self.end_headers()
      elif self.path == '/index.html':
          content = PAGE.encode('utf-8')
          self.send_response(200)
          self.send_header('Content-Type', 'text/html')
          self.send_header('Content-Length', len(content))
          self.end_headers()
          self.wfile.write(content)
      elif self.path == '/stream.mjpg':
          self.send_response(200)
          self.send_header('Age', 0)
          self.send_header('Cache-Control', 'no-cache, private')
          self.send_header('Pragma', 'no-cache')
          self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
          self.end_headers()
          try:
              while True:
                  with output.condition:
                      output.condition.wait()
                      frame = output.frame
                  self.wfile.write(b'--FRAME\r\n')
                  self.send_header('Content-Type', 'image/jpeg')
                  self.send_header('Content-Length', len(frame))
                  self.end_headers()
                  self.wfile.write(frame)
                  self.wfile.write(b'\r\n')
          except Exception as e:
              logging.warning(
                  'Removed streaming client %s: %s',
                  self.client_address, str(e))
      else:
          self.send_error(404)
          self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


print("Attempting camera connection...")
with picamera.PiCamera(resolution='1640x1232', framerate=24) as camera:
    output = StreamingOutput()
    print("Set streaming output")

    # Set the generic/standard camera props
    camera.rotation = 180

    # Actually start the show
    print("Starting recording!")
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8675)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()
        print("Stopped recording")

print("Exited! Camera object should be closed now")
