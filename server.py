import socket
import threading
import re
import ssl
import sys 
import requests

PORT = 2009
IP = '0.0.0.0'
CLIENT_SOCKET_TIMEOUT = 15
SERVER_SOCKET_TIMEOUT = 1
CLIENT_DICT = {}
MAX_CONN_Q = 5
BUFFER_SIZE = 2048
HTTP = 80
HTTPS = 443
class Proxy:

    def __init__(self):
        self.is_SSL = False

    def forward_request(self, request, url, port):
        req_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.is_SSL:
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            secure_socket = context.wrap_socket(req_socket, server_hostname=url)
            addr = (url, port)
            print(addr)
            secure_socket.connect(addr)
            secure_socket.send(request.encode())
            resp = self.receive_socket_data(secure_socket)
            secure_socket.close()
        else:
            addr = (url, port)
            print(addr)
            req_socket.connect(addr)
            req_socket.send(request.encode())
            req_socket.settimeout(CLIENT_SOCKET_TIMEOUT)
            resp = self.receive_socket_data(req_socket)
            req_socket.close()
        return resp

    def isolate_url(self,request):
        request_method, url = request.split()[:2]
        if request_method == 'CONNECT':
            self.is_SSL = True
            print("SSL TRUE: Printing Reuquest:")
            print(request)
            url, port = url.split(':')[:2]
            print("URL:")
            print(url)
            return url, int(port)
        else:
            self.is_SSL = False
            print("Printing Reuquest:")
            print(request)
            url = url.strip("http://")
            return url, 80
   
    def establish_connection(self, url):
        # response = requests.get("https://{0}".format(url), stream=True)
        request_header = "GET / HTTP/1.1\r\nHost:{0}\r\n\r\n".format(url)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (url, HTTPS)

        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        secure_socket = context.wrap_socket(s, server_hostname=url)
        secure_socket.connect(server_address)
        secure_socket.send(request_header.encode())

        response = self.receive_socket_data(secure_socket)
        s.close()
        return response
        

    def receive_socket_data(self, client_socket):
        client_request = ""
        client_socket.settimeout(0.5)
        while True:
            try:
                data = client_socket.recv(BUFFER_SIZE)
                client_request += data.decode()
            except Exception:
                break
            if not data:
                # either 0 or end of data
                break
        
        return client_request

    def handle_client(self,socket, addr):
        try:
            client_request = self.receive_socket_data(socket)
            url,port = self.isolate_url(client_request)
            print(client_request)
            if self.is_SSL:
                resp = self.establish_connection(url)
                print("RESPONSE: \n" + resp)
                print("Response Size: {0}".format(len(resp)))
            else:
                resp = self.forward_request(client_request, url, port)
                print("RESPONSE: \n" + resp)
            
            socket.send(resp.encode())
            socket.close()
            print("[*] {0} connection closed".format(addr))
        except KeyboardInterrupt:
            print("\n[*] User Requested an Interrupt ")
            print("[*] Application Exiting...")
            sys.exit()



    def main(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((IP,PORT))
        server_socket.listen(MAX_CONN_Q)
        print('[*] Listening For Connections on Port {0}'.format(PORT))
    
        while True:
            try:
                client_socket, client_addr = server_socket.accept()
                print('[*] New Connection Received From {0}'.format(client_addr))
                client_socket.settimeout(CLIENT_SOCKET_TIMEOUT)
                p1 = threading.Thread(target=self.handle_client, args=(client_socket,client_addr))
                p1.start()
                # self.handle_client(client_socket, client_addr)

            except KeyboardInterrupt:
                client_socket.close()
                print("\n[*] User Requested an Interrupt ")
                print("[*] Application Exiting...")
                sys.exit()


if __name__ == "__main__":
  proxy = Proxy()
  proxy.main()
