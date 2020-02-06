#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# Copyright 2020 Ken Li
#  
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    # Return host and port from url
    def get_host_port(self, url):
        parseObj = urllib.parse.urlparse(url)

        scheme = parseObj.scheme
        path = parseObj.path
        host = parseObj.hostname
        port = parseObj.port

        if (not path):
            path = "/"

        if (not port):
            if (scheme == "https"):
                port = 443
            else:
                port = 80

        return host, port, path

    # Connect to host using port
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        
    # Send request
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    # Read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    # Get HTTP status code
    def get_code(self, data):
        return int(data.split(' ')[1])

    # Get HTML headers
    def get_headers(self, data):
        return data.split("\r\n\r\n")[0]

    # Get HTML body content
    def get_body(self, data):
        return data.split("\r\n\r\n")[1]

    # Close socket
    def close(self):
        self.socket.close()

    # Calls POST or GET commad depending on command line args
    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

    def GET(self, url, args=None):
        # Connect to host using port
        host, port, path = self.get_host_port(url)
        self.connect(host, port)

        # Send request
        request = "GET " + path + " HTTP/1.1\r\nHost: " + host + "\r\nConnection: close" + "\r\n\r\n"
        self.sendall(request)

        # Get response
        response = self.recvall(self.socket)

        # Parse response
        code = self.get_code(response)
        header = self.get_headers(response)
        body = self.get_body(response)

        # Close socket
        self.close()

        print(body)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # Connect to host using port
        host, port, path = self.get_host_port(url)
        self.connect(host, port)

        # Convert None to empty
        if (args == None):
            args = ''
        encodedArgs = urllib.parse.urlencode(args)

        # Send request
        protocol = "POST " + path + " HTTP/1.1\r\n"
        host = "Host: " + host + "\r\n"
        contentType = "Content-Type: application/x-www-form-urlencoded\r\n"
        contentLength = "Content-Length: " + str(len(encodedArgs)) + "\r\n"
        connectionType = "Connection: close\r\n"
        content = "\r\n" + encodedArgs
        
        request = protocol + host + contentType + contentLength + connectionType + content
        self.sendall(request)

        # Get response
        response = self.recvall(self.socket)

        code = self.get_code(response)
        header = self.get_headers(response)
        body = self.get_body(response)

        self.close()

        print(body)

        return HTTPResponse(code, body)
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"

    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
