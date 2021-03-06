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
from PyQt4.QtCore import QString
from PyQt4.QtCore import QThread
from PyQt4.QtGui import qApp
from PyQt4.QtGui import QMenu
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QPrinter
from PyQt4.QtGui import QPrintDialog
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
            if ' % ' in self.command:
                cmd = self.command.replace(' % ', ' %s ' % filename)
            else:
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
            self._view.setContextMenuPolicy(Qt.CustomContextMenu)
            QObject.connect(self._view, SIGNAL("update(QString)"), self._update)

            def openMenu(position):
                menu = QMenu()
                printAction = menu.addAction("Print")
                quitAction = menu.addAction("Quit")
                action = menu.exec_(self._view.mapToGlobal(position))

                if action == quitAction:
                    qApp.quit()
                elif action == printAction:
                    printer = QPrinter()
                    dialog = QPrintDialog(printer, self._view)
                    if dialog.exec_() != QDialog.Accepted:
                        return
                    self._view.print_(printer)
            self._view.customContextMenuRequested.connect(openMenu)

        def _update(self, html):
            mainFrame = self._view.page().mainFrame()
            v = mainFrame.scrollBarValue(Qt.Vertical)
            h = mainFrame.scrollBarValue(Qt.Horizontal)
            self._view.setHtml(QString.fromUtf8(html))
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
            def update_preview(self, qs):
                qs = urlparse.parse_qs(qs, 1)
                filename = qs.get('filename', ['README.markdown'])[0]
                # compile via pandoc
                data = compiler.compile(filename)
                # update preview
                viewer._view.emit(SIGNAL('update(QString)'), data)
                return data

            def do_GET(self):
                try:
                    if self.path == '/favicon.ico':
                        return
                    # get pandoc filename from query string
                    qs = urlparse.urlparse(self.path).query
                    data = self.update_preview(qs)
                    # respond data
                    self.wfile.write(data)
                except Exception, e:
                    print "Error:", e
                    self.wfile.write("Unexpected error: %s" % e)

            def do_POST(self):
                try:
                    # get pandoc filename from query string
                    qs = self.rfile.read(int(self.headers.getheader('Content-Length')))
                    self.update_preview(qs)
                    # respond OK
                    self.wfile.write('OK')
                except Exception, e:
                    print "Error:", e
                    self.wfile.write("Unexpected error: %s" % e)

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
