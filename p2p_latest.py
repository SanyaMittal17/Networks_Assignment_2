import socket
import threading
import logging
from time import sleep
global lines 
global reply
global lim
lines = {}
lim=1000
reply='0'
svayu = socket.socket()
svayu.connect(("vayu.iitd.ac.in", 9801))
def handle_client(client_socket, client_address):
    global lines 
    global reply
    global lim
    print("Connected by", client_address)
    while reply!='1':
        try:
            data=""
            while(True):
                data_new= client_socket.recv(4096).decode('utf-8')
                data+=data_new
                if(not data_new or data[-1]=='\n'): break
            if not data: continue
            try:
                line_no, line, *_ = map(str,data.split('\n')) 
                line_no = int(line_no)
                if(line_no==-1): continue
            except: 
                client_socket.sendall(reply.encode())
                continue
            if line_no not in lines.keys(): 
                lines[line_no] = line
                logging.warning(len(lines))
            l=len(lines)
            if(l==lim): reply='1'
            client_socket.sendall(reply.encode())
        except Exception as e:
            print("error: ", e)
            print(data)
    print("Thread Closed")
    client_socket.close()

def my_client():
    global svayu
    while True:
        try:
            svayu.sendall(b"SENDLINE\n")
            response=""
            while(True):
                response_new= svayu.recv(4096).decode('utf-8')
                response+=response_new
                if(not response_new or response_new[-1]=='\n'): break
        except Exception as e:
            continue
        reply=sendline(response)
        if (reply=="1"):
            break
    print("Thread Closed")

def sendline(data):
    global lines
    global reply
    global lim
    if not data: return '0'
    try:
        line_no, line, *_ = map(str,data.split('\n'))
        if(line_no=="-1"): return '0'
        line_no = int(line_no)
    except: return '0'
    if(line_no==-1): return '0'
    if line_no not in lines.keys(): 
        lines[line_no] = line
        logging.warning(len(lines))
    l=len(lines)
    if(l==lim): reply='1'
    return reply

def main():
    global reply
    global lines
    global svayu
    server_ip = '10.194.25.90'  # Listen on all available interfaces
    base_port = 12345
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, base_port))
    server_socket.listen(5)
    print("Server is listening for incoming connections...")
    my_thread = threading.Thread(target=my_client)
    client_socket, client_address = server_socket.accept()
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_socket1, client_address1 = server_socket.accept()
    client_thread1 = threading.Thread(target=handle_client, args=(client_socket1, client_address1))
    client_thread1.start()
    print("Starting the thread")
    my_thread.start()
    client_thread.start()
    while(reply!='1'):
        pass
    # client_socket2, client_address2 = server_socket.accept()
    # client_thread2 = threading.Thread(target=handle_client, args=(client_socket2, client_address2))
    # client_thread2.start() 
    print("Done receiving")
    server_socket.close()
    with open('output.txt', "w") as f:
        for i in range(0,1000):
            f.write(lines[i]+ '\n')
    print("starting to submit the lines")
    svayu.sendall(b"SUBMIT\nKASHISH@COL334-672\n1000\n")
    for i in range(0,1000):
        line=f"{i}\n{lines[i]}\n"
        svayu.sendall(line.encode())
    resp=svayu.recv(4096).decode('utf-8').split()
    print(resp)
    svayu.close()
    client_thread1.join()
    client_thread.join()
    # print('\n'.join(lines.values()))
if __name__ == "__main__":
    main()
