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

import sys
import socket
import re
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_payload(self, host, path):
        payload = "GET {PATH} HTTP/1.1\r\n".format( PATH=path)
        payload += "Host: {HOST}\r\n".format(HOST=host)
        payload += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
        payload += "Accept-Charset: utf-8\r\n"
        payload += "Accept-Language: en-US,en;q=0.5\r\n"
        payload += "Connection: close\r\n\r\n"
        return payload

    def post_payload(self, host, path, body):
        payload = "POST {PATH} HTTP/1.1\r\n".format(PATH=path)
        payload += "Host: {HOST}\r\n".format(HOST=host)
        payload += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
        payload += "Accept-Language: en-US\r\n"
        payload += "Connection: close\r\n"

        length = "0"
        if body is not None:
            payload += "Content-Type: application/x-www-form-urlencoded\r\n"
            length = len(body)

        payload += "Content-Length: {LENGTH}\r\n".format(LENGTH=length)
        payload += "\r\n"

        if body is not None:
            payload += "{BODY}\r\n".format(BODY=body)

        return payload

    # Retrieve the response status code
    def get_code(self, data):
        header = data.split("\r\n\r\n")[0]
        status_line = header.split("\r\n")[0]
        status_code = status_line.split(" ")[1]
        return int(status_code)

    # Parse the response headers into a dictionary
    def get_headers(self, data):
        header_dict = dict()
        header = data.split("\r\n\r\n")[0]
        headers = data.split("\r\n")[1:] # Ignore status line
        for header in headers:
            elements = header.split(":")
            key = elements[0]

            # TODO: Should probably find a way to parse this properly
            values = elements[1:]

            header_dict[key] = values
        return header_dict

    def get_body(self, data):
        data = data.split("\r\n\r\n")
        if (len(data) > 1):
            return data[1]
        else:
            return None

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
        url = urllib.parse.urlparse(url)

        port = 80
        if url.port is not None:
            port = url.port

        path = url.path
        if path == "":
            path = "/"

        self.connect(url.hostname, port)
        self.sendall(self.get_payload(url.hostname, path))
        response_data = str(self.recvall(self.socket))
        self.close()

        body = self.get_body(response_data)
        code = self.get_code(response_data)
        print(body);
        
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        url = urllib.parse.urlparse(url)

        port = 80
        if url.port is not None:
            port = url.port

        path = url.path
        if path == "":
            path = "/"

        body = None
        if args is not None:
            body = urllib.parse.urlencode(args)

        self.connect(url.hostname, port)
        self.sendall(self.post_payload(url.hostname, path, body))
        response_data = str(self.recvall(self.socket))
        self.close()

        body = self.get_body(response_data)
        code = self.get_code(response_data)
        print(body)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)

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
