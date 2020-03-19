import socket
import sys
import threading

BUFFER_SIZE = 4096
MAX_CONN = 5
LISTENING_PORT = 2009


def conn_string(conn, data, addr):
    # try:
    first_line = data.split('\r\n')[0]
    url = first_line.split(' ')[1]
    http_pos = url.find("://")
    if http_pos == -1:
        temp = url
    else:
        temp = url[(http_pos+3):]
    port_pos = temp.find(":")
    webserver_pos = temp.find("/")
    if webserver_pos == -1:
        webserver_pos = len(temp)
    webserver = ""
    port = -1
    if port_pos == -1 or webserver_pos < port_pos:
        port = 80
        webserver = temp[:webserver_pos]
    else:
        port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
        webserver = temp[:port_pos]
    proxy_server(webserver, port, conn, addr, data)
    # except Exception as e:
    #     print("[*] Error")
    #     print(e)
    #     pass

def proxy_server(webserver, port, conn, addr, data):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((webserver, port))
        s.send(data.encode())
        while True:
            reply = s.recv(BUFFER_SIZE)
            print("[*] Server Reply:\n{0}".format(reply.decode()))
            if len(reply) > 0:
                conn.send(reply)
                dar = float(len(reply))
                dar = float(dar / 1024)
                dar = "%.3s" % str(dar)
                dar = "%s KB" % dar
                print("[*] Request Done: %s => %s <=" % (str(addr[0]), str(dar)))
            else:
                break
        s.close()
        conn.close()
    except socket.error as err:
        print(err)
        s.close()
        conn.close()
        sys.exit(1)


def start():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('0.0.0.0', LISTENING_PORT))
        s.listen(MAX_CONN)
        print("[*] Initializing Sockets")
        print("[*] Server Listening on Port {0}".format(str(LISTENING_PORT)))
    except Exception as e:
        print("[*] Unable to Initialize Socket\n[*]{0}".format(str(e)))
        sys.exit(2)

    while True:
        try:
            conn, addr = s.accept()
            data = conn.recv(BUFFER_SIZE)
            # conn_string(conn, data.decode(), addr)
            p1 = threading.Thread(target=conn_string, args=(conn, data.decode(), addr))
            p1.start()
            print(data.decode())
        except KeyboardInterrupt:
            s.close()
            print("[*] Interupt Detected...Proxy Shutting Down")
            sys.exit(1)
    s.close()

if __name__ == "__main__":
    start()



            




            





