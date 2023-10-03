import socket
import logging
from multiprocess import Manager, Process, Value

# Define global variables
manager = Manager()
lines = manager.dict()
lim = 1000
reply = Value('i', 0)
svayu = None
def handle_client_done(client_socket,):
    global reply
    while reply.value!=1:
        continue
    rec=b'0'
    while rec!=b'1':
        try:
            client_socket.sendall(b"1")
            rec=client_socket.recv(4096)
        except:
            continue
    client_socket.close()
    print("Thread Closed")
def handle_client(client_socket, client_socket_2):
    global lines 
    global reply
    global lim
    client_reply_thread=Process(target=handle_client_done, args=(client_socket_2,))
    client_reply_thread.start()
    while reply.value!=1:
        try:
            data=b""
            while(True):
                data_new= client_socket.recv(4096)
                data+=data_new
                if(not data_new or data_new[-1]==10): break
            try:
                line_no, line,_ = data.split(b'\n')
                if(line_no==b'-1'): continue
            except: 
                continue
            if line_no not in lines.keys(): 
                lines[line_no] = (line_no+b'\n'+line+b'\n')
                logging.warning(len(lines))
            if(len(lines)==lim): reply.value=1
        except Exception as e:
            print("error: ", e)
            print(data)
    print("Thread Closed")
    client_socket.close()

def my_client():
    global svayu
    global reply
    while True:
        try:
            svayu.sendall(b"SENDLINE\n")
            response=b""
            while(True):
                response_new= svayu.recv(4096)
                response+=response_new
                if(not response_new or response_new[-1]==10): break
        except Exception as e:
            continue
        sendline(response)
        if (reply.value==1):
            break
    print("Thread Closed")


def sendline(data):
    global lines
    global reply
    global lim
    if not data: return
    try:
        line_no, line,_ = data.split(b'\n')
        if(line_no==b'-1'): return
    except Exception as e: 
        print("error: "+str(e))
        return 
    if line_no not in lines.keys(): 
        lines[line_no] = (line_no+b'\n'+line+b'\n')
        logging.warning(len(lines))
    if(len(lines)==lim): reply.value=1

def wait():
    global reply
    while reply.value!=1:
        continue

def main():
    global reply
    global lines
    global svayu
    server_ip = '10.194.1.207'  # Listen on all available interfaces
    base_port = 8001
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, base_port))
    server_socket.listen(1)
    server_socket_done = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket_done.bind((server_ip, base_port+1000))
    server_socket_done.listen(1)
    # server_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # base_port1 = 8002
    # server_socket1.bind((server_ip, base_port1))
    # server_socket1.listen(1)
    # server_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # base_port2 = 8003
    # server_socket2.bind((server_ip, base_port2))
    # server_socket2.listen(1)
    print("Server is listening for incoming connections...")
    my_thread = Process(target=my_client)
    client_socket, client_address = server_socket.accept()
    client_socket_done, client_address_done = server_socket_done.accept()
    client_thread = Process(target=handle_client, args=(client_socket, client_socket_done))
    # client_socket1, client_address1 = server_socket1.accept()
    # client_thread1 = Process(target=handle_client, args=(client_socket1, client_address1))
    # client_socket2, client_address2 = server_socket2.accept()
    # client_thread2 = Process(target=handle_client, args=(client_socket2, client_address2))
    wait_thread=Process(target=wait)
    print("Starting the thread")
    client_socket.sendall(b"OK")
    # client_socket1.sendall(b"OK")
    # client_socket2.sendall(b"OK")
    svayu = socket.socket()
    svayu.connect(("10.17.6.5", 9801))
    svayu.sendall(b"SESSION RESET\n")
    reply1=svayu.recv(4096)
    my_thread.start()
    client_thread.start()
    # client_thread1.start()
    # client_thread2.start()
    wait_thread.start()
    wait_thread.join()
    print("Done receiving")
    server_socket.close()
    print("starting to submit the lines")
    svayu.sendall(b"SUBMIT\nKASHISH@COL334-672\n1000\n")
    for line in lines.values():
        svayu.sendall(line)
    resp=svayu.recv(4096).decode('utf-8')
    print(resp)
    svayu.close()
    reply.value=1
    my_thread.join()
    reply.value=1
    client_thread.join()
    # reply.value=1
    # client_thread1.join()
    # reply.value=1
    # client_thread2.join()
if __name__ == "__main__":
    main()
