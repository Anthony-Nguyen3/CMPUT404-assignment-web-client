#!/usr/bin/env python3
# coding: utf-8
# Copyright 2022 Anthony Nguyen
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
# you may use urllib to encode data appropriately
import urllib.parse

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
        # Get header first
        split_data = data.split("\r\n\r\n")
        header = split_data[0]

        # get code from header
        split_header = header.split(" ")

        # code is 2nd argument, HTTP/1.1 [code] [message] ....
        code = int(split_header[1])
        return code

    def get_headers(self,data):
        # Body and head is spearataed by a blank line
        split_data = data.split("\r\n\r\n")
        header = split_data[0]
        return header

    def get_body(self, data):
        # Body and head is spearataed by a blank line
        split_data = data.split("\r\n\r\n")
        body = split_data[1]
        return body
    
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
        parsed_url = urllib.parse.urlparse(url)

        # get the host name
        host_name = parsed_url.hostname

        # get the port number, default is 80
        port = parsed_url.port
        if port is None:
            port = 80

        # get the path to send request, default is  /
        path = parsed_url.path
        if path == '':
            path = '/'
            
        # connect to socket
        self.connect(host_name, port)

         # send GET request
        request_str = "GET " + path + " HTTP/1.1\r\nHost: " + host_name + "\r\n" + "Connection: close\r\n\r\n"
        self.sendall(request_str)
        
        # get response body as a string
        response_str = self.recvall(self.socket)

        # extract HTTP code and response body
        code = self.get_code(response_str)
        body = self.get_body(response_str)

        print(response_str)

        # close connection
        self.close()
        
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        parsed_url = urllib.parse.urlparse(url)

        # get the host name
        host_name = parsed_url.hostname

        # get the port number, default is 80
        port = parsed_url.port
        if port is None:
            port = 80

        # get the path to send request, default is  /
        path = parsed_url.path
        if path == '':
            path = '/'
            
        # connect to socket
        self.connect(host_name, port)

        # send post request body
        request_body = ''
        if args is not None:
            request_body = urllib.parse.urlencode(args)

        # send POST request headers
        request_str = "POST " + path + " HTTP/1.1\r\nHost: " + host_name + "\r\n" +"User-Agent: " + "httpclient/1.0" + "\r\n" + "Content-Type: application/x-www-form-urlencoded\r\n" + "Content-Length: " + str(len(request_body)) + "\r\n" + "Connection: close\r\n\r\n"
        request_str += request_body
        self.sendall(request_str)
        
        # get response body as a string
        response_str = self.recvall(self.socket)

        # extract HTTP code and response body
        code = self.get_code(response_str)
        body = self.get_body(response_str)

        print(response_str)

        # close connection
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
