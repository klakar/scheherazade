# -*- coding: utf-8 -*-
import os
import SimpleHTTPServer
import SocketServer

def infolder(storyFolder):
	os.chdir(storyFolder)
	Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
	httpd = SocketServer.TCPServer(("localhost", 8080), Handler)
	httpd.serve_forever()