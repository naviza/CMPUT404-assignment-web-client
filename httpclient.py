#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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


"""
Sources:
- https://reqbin.com/req/nfilsyk5/get-request-example
- Class's forum discussion
- Class's Discord server discussion

"""

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

DEFAULT_SOCKET = 8001

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        first_line = re.split('\\r\\n', data)[0]
        # Assuming that the response is valid, code should be the second value
        return re.split(' ', first_line)[1]

    def get_headers(self,data):
        return None

    def get_body(self, data):
        # Assuming that the response is valid, body comes after the \r\n\r\n
        return re.split('\\r\\n\\r\\n', data)[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
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

    def GET(self, url, args=None):
        """
            GET /echo HTTP/1.1
            Host: reqbin.com
            Connection: close


        """
        # Documentation: https://docs.python.org/3/library/urllib.parse.html
        parsed_url = urllib.parse.urlparse(url)

        get_line = "GET " + (parsed_url.path if parsed_url.path else "/") + " HTTP/1.1\r\n"
        host_line = "Host: " + parsed_url.hostname + "\r\n"
        connection_line = "Connection: close\r\n\r\n"
        # accept_line = "Accept: text/html;charset=utf-8, */*\r\n\r\n"

        data_to_send = get_line + host_line + connection_line
        # print(data_to_send)

        if parsed_url.port:
            self.connect(parsed_url.hostname, parsed_url.port)
        elif parsed_url.scheme == "https":
            self.connect(parsed_url.hostname, 443)
        else: # http
            self.connect(parsed_url.hostname, 80)

        # self.socket.sendall((get_line + host_line + accept_line).encode('utf-8'))
        self.sendall(data_to_send)

        data = self.recvall(self.socket)
        # print(data)
        code = int(self.get_code(data))
        body = self.get_body(data)
        self.close()

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        """
            https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST

            POST /test HTTP/1.1
            Host: foo.example
            Content-Type: application/x-www-form-urlencoded
            Content-Length: 27

            field1=value1&field2=value2
        """

        parsed_url = urllib.parse.urlparse(url)

        post_line = "POST " + (parsed_url.path if parsed_url.path else "/") + " HTTP/1.1\r\n"
        host_line = "Host: " + parsed_url.hostname + "\r\n"
        content_type_line = "Content-Type: application/x-www-form-urlencoded\r\n"
        # connection_line = "Connection: close\r\n\r\n"
        
        if args is not None:
            parameters_line = urllib.parse.urlencode(args)
            parameters_length = len(parameters_line)
            content_length_line = "Content-Length: " + str(parameters_length) + "\r\n\r\n"
        else:
            parameters_line = ""
            content_length_line = "Content-Length: 0\r\n\r\n"

        data_to_send = post_line + host_line + content_type_line + content_length_line + parameters_line + "\r\n"

        if parsed_url.port:
            self.connect(parsed_url.hostname, parsed_url.port)
        elif parsed_url.scheme == "https":
            self.connect(parsed_url.hostname, 443)
        else: # http
            self.connect(parsed_url.hostname, 80)

        # self.socket.sendall((get_line + host_line + accept_line).encode('utf-8'))
        self.sendall(data_to_send)

        data = self.recvall(self.socket)
        # print(data)
        code = int(self.get_code(data))
        body = self.get_body(data)
        self.close()

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
