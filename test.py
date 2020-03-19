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
        self.isCONNECT = False

    def forward_request(self, browser_socket, server_socket):
        while True:
            try:
                data = browser_socket.recv(BUFFER_SIZE)
                server_socket.sendall(data)
                print("DATA:")
            except socket.error as err:
                print("ERROR:" + str(err))
                break
            try:
                reply = server_socket.recv(BUFFER_SIZE)
                browser_socket.sendall(reply)
                print("REPLY DATA:")
            except socket.error as err:
                print("ERROR:" + str(err))
                break
        
        

    def isolate_url(self,request):
        request_method, url = request.split()[:2]
        if request_method == 'CONNECT':
            self.isCONNECT = True
            print("SSL TRUE: Printing Reuquest:")
            print(request)
            url, port = url.split(':')[:2]
            print("URL: {0}\nPORT: {1}".format(url, port))
            return url, int(port)
        else:
            self.isCONNECT = False
            lines = request.split('\r\n')
            url = ''
            for i in lines:
                if re.search(r'Host:', i):
                    host = i
            host = host.strip("Host: ")
            print("HOST: " + host)
            print("############GIVING INFO JUST PASS IT ON############### \n Printing Request:")
            return url, HTTP
   
    def start_tunneling(self, url, port, client_request):
        # response = requests.get("https://{0}".format(url), stream=True)
        request_headers = client_request.split('\r\n')[1:-1:1]
        headers = '\r\n'.join(request_headers)
        
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.settimeout(CLIENT_SOCKET_TIMEOUT)
        server_address = (url, port)

        try:
            server_socket.connect(server_address)
            reply_browser = "HTTP/1.1 200 Connection established\r\n\r\n" #+ headers
            #reply_browser += "Transfer-Encoding: chunked\r\n"
            #reply_browser += "Content-Type: text/html\r\n\r\n"

        except socket.error as err:
            print(err)

        print("REPLY TO BROWSER:\n{0} ".format(reply_browser))

        # secure_socket.close()
        return reply_browser, server_socket
        

    def receive_socket_data(self, client_socket):
        client_request = ""
        # client_socket.settimeout(0.5)
        while True:
            data = client_socket.recv(BUFFER_SIZE)
            if len(data) < 1:
                # either 0 or end of data
                break
            client_request += data.decode()

        
        return client_request
    
    def handle_client(self,client_socket, addr):
        try:
            
            client_request = self.receive_socket_data(client_socket)
            url,port = self.isolate_url(client_request)
            if self.isCONNECT:
                #Do a HTTP Tunnel
                print(client_request)
                browser_reply, server_socket = self.start_tunneling(url, port, client_request)
                client_socket.send(browser_reply.encode())
                
                #Forwarding Bytes
                self.forward_request(client_socket, server_socket)
            else:
                #Single HTTP Request
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    server_socket.connect((url, port))
                    server_socket.sendall(client_request.encode())
                    request = self.receive_socket_data(server_socket)
                except socket.error as err:
                    print(err)
                    secure_socket = ssl.wrap_socket(server_socket, ssl_version=ssl.PROTOCOL_TLSv1_2)
                    secure_socket.connect((url, HTTPS))
                    secure_socket.sendall(client_request.encode())
                    request = self.receive_socket_data(secure_socket)
                
                client_socket.sendall(request.encode())


            #When done close connection
            server_socket.close()
            client_socket.close()
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
                # p1 = threading.Thread(target=self.handle_client, args=(client_socket,client_addr))
                # p1.start()
                self.handle_client(client_socket, client_addr)

            except KeyboardInterrupt:
                client_socket.close()
                print("\n[*] User Requested an Interrupt ")
                print("[*] Application Exiting...")
                sys.exit()


if __name__ == "__main__":
  proxy = Proxy()
  proxy.main()
