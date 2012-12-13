#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
import sys
import socket
import urlparse
import commands
from optparse import OptionParser
from BaseHTTPServer import HTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler
from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QObject
from PyQt4.QtCore import QThread
from PyQt4.QtGui import QApplication
from PyQt4.QtWebKit import QWebView
from PyQt4.QtNetwork import QNetworkProxyFactory


HOST = '127.0.0.1'
PORT = 8081
COMMAND = 'pandoc -t html -Ss --toc'


def is_running(host, port):
    s = socket.socket()
    try:
        s.settimeout(1)
        s.connect((host, port))
        return True
    except socket.error:
        return False


def start(host, port, command):
    class Compiler(object):
        def __init__(self, command):
            self.command = command

        def compile(self, filename):
            cmd = self.command + ' ' + filename
            status, output = commands.getstatusoutput(cmd)
            return output
    compiler = Compiler(command)

    class Viewer(object):
        def __init__(self):
            # Use System proxy configuration
            QNetworkProxyFactory.setUseSystemConfiguration(True)
            self._app = QApplication(sys.argv)
            self._view = QWebView()
            QObject.connect(self._view, SIGNAL("update(QString)"), self._update)

        def _update(self, html):
            mainFrame = self._view.page().mainFrame()
            v = mainFrame.scrollBarValue(Qt.Vertical)
            h = mainFrame.scrollBarValue(Qt.Horizontal)
            self._view.setHtml(html)
            mainFrame = self._view.page().mainFrame()
            mainFrame.setScrollBarValue(Qt.Vertical, v)
            mainFrame.setScrollBarValue(Qt.Horizontal, h)

        def start(self):
            self._view.setWindowTitle('Preview')
            self._view.show()

            sys.exit(self._app.exec_())
    viewer = Viewer()

    class Server(QThread):
        class HTTPPreviewRequestHandler(BaseHTTPRequestHandler):
            def do_POST(self):
                if self.path == '/favicon.ico':
                    return
                # get pandoc filename from query string
                #qs = urlparse.urlparse(self.path).query
                qs = self.rfile.read(int(self.headers.getheader('Content-Length')))
                qs = urlparse.parse_qs(qs, 1)
                filename = qs.get('filename', ['README.markdown'])[0]
                # compile via pandoc
                data = compiler.compile(filename)
                # update preview
                viewer._view.emit(SIGNAL('update(QString)'), data)
                # respond
                self.wfile.write('OK')

        def __init__(self, host, port):
            super(Server, self).__init__()
            self.host = host
            self.port = port
            self.httpd = HTTPServer((self.host, self.port), self.HTTPPreviewRequestHandler)

        def run(self):
            self.httpd.serve_forever()
    server = Server(host, port)

    server.start()
    viewer.start()


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-o', '--host', dest='host', default=str(HOST),
                      help='Start preview request server at HOST', metavar='HOST')
    parser.add_option('-p', '--port', dest='port', default=str(PORT),
                      help='Start preview request server at PORT', metavar='PORT')
    parser.add_option('-c', '--command', dest='command', default=str(COMMAND),
                      help='Command used for compiling pandoc file')
    opts, args = parser.parse_args()
    host = opts.host
    port = int(opts.port)
    command = opts.command

    if not is_running(host, port):
        start(host, port, command)
    else:
        exit(1)
