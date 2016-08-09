'''
Not sure the code is 100% effective. It comes from several sources and combined by me.
Call "create" with arguments [1] IP or localhost, [2] port to serve on
Call "start" to start the thread
Call "stop" to stop the thread
'''

import threading
import thread
import sys
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from SocketServer import ThreadingMixIn


class ThreadingServer(ThreadingMixIn, HTTPServer):
    pass

class TinyWebServer(object):

    def create(self, ip_addr, port): # Create the web server
        serveraddr = (ip_addr, port)
        self.httpd = ThreadingServer(serveraddr, SimpleHTTPRequestHandler)

    def start(self): # Start the web server
        """
        start the web server on a new thread
        """
        self._webserver_died = threading.Event()
        self._webserver_thread = threading.Thread(
                target=self._run_webserver_thread)
        self._webserver_thread.start()

    def _run_webserver_thread(self): # run the thread
        self.httpd.serve_forever()
        self._webserver_died.set()

    def stop(self): # Stop Simple HTTP Server thread
        if not self._webserver_thread:
            return
        thread.start_new_thread(self.httpd.shutdown, () )
