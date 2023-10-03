import socket
import threading
import logging
import time
from queue import Queue

clients_send={}
clients_recv={}
done={}
queues={} # queues[id] is the queue for client id
lines={} 
lim=1000
num_clients=1
active_clients_send=0
active_clients_recv=0

global vayutime, vayucount
vayutime, vayucount = 0,0

my_ip='10.194.4.246'
my_port_begin=8000
vayu_ip='10.17.7.218'
vayu_port=9801
vayu_=(vayu_ip,vayu_port)

def vayu_connect():
    global vayu_socket
    global vayu_
    vayu_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    vayu_socket.connect(vayu_)
    vayu_socket.sendall(b"SESSION RESET\n")
    reply=vayu_socket.recv(4096)
    while(not reply):
        try:
            vayu_socket.close()
        except:
            pass
        try:
            vayu_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            vayu_socket.connect(vayu_)
            vayu_socket.sendall(b"SESSION RESET\n")
            reply=vayu_socket.recv(4096)
        except:
            time.sleep(0.001)
            continue
    # print("exited the vayu connect funtcion ")
    
def client_connect_send(id):
    global clients_send
    global queues
    global done
    global active_clients_send
    # opens a connection with the id_ client for sending
    _socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _socket.bind((my_ip,my_port_begin+id))
    _socket.listen(1)
    done[id]=False
    queues[id]=Queue()
    id_=bytes(str(id),'utf-8')+b'#1'
    i = 0
    while(not done[id]):
        print("waiting for client "+str(id))
        try:
            conn, addr=_socket.accept()
            reply=conn.recv(4096)
            if(reply!=id_):
                print("bt")
                conn.close()
                continue
            for _ in range(10):
                print("hi")
                try:
                    conn.sendall(b"OK")
                    if(id in clients_send):
                        try:
                            print("active user inc")
                            clients_send[id].close()
                            active_clients_send-=1
                        except:
                            print("in the except where pass has been used")
                            pass
                    clients_send[id]=conn
                    active_clients_send+=1
                    logging.warning("connected to client for send "+str(id))
                    print("going to the break statemtn which will end the for loop")
                    break
                except:
                    time.sleep(0.001)
                    continue 
        except:
            try:
                conn.close()
            except:
                print("in the except of except ")
                pass
            time.sleep(0.001)
            continue
        time.sleep(0.001)
        i += 1
    print(done[id])
    print("dshgvfrshugeshu")
    print("exited the client connect send function ")
    clients_send[id].close()
    _socket.close()
    print("exited the client connect send function ")
    return 

def client_connect_recv(id):
    global clients_recv
    global queues
    global done
    global lines
    global lim
    global active_clients_recv
    # opens a connection with the id_ client for sending
    _socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _socket.bind((my_ip,my_port_begin+id+1000))
    _socket.listen(1)
    id_=bytes(str(id),'utf-8')+b'#2'
    while(len(lines)<lim):
        try:
            conn, addr=_socket.accept()
            reply=conn.recv(4096)
            if(reply!=id_):
                conn.close()
                continue
            for _ in range(10):
                try:
                    conn.sendall(b"OK")
                    if(id in clients_recv):
                        try:
                            clients_recv[id].close()
                            active_clients_recv-=1
                        except:
                            pass
                    clients_recv[id]=conn
                    active_clients_recv+=1
                    logging.warning("connected to client for recv "+str(id))
                    break
                except:
                    continue 
        except:
            try:
                conn.close()
            except:
                pass
            continue
    while not done[id]:
        time.sleep(0.001)
    clients_recv[id].close()
    _socket.close()
    print("exited the client connect recv function ")             

def send_to_client(id):
    #sends the messages in the queue of client id to the client
    global queues
    global clients_recv
    global done
    global lines
    global lim
    global active_clients

    curr_queue = queues[id]
    curr_socket = clients_recv[id]
    # curr_socket.settimeout(0.5)
    while not done[id]:
        while curr_queue.qsize() > 0:
            msg = curr_queue.get()
            try:
                curr_socket.sendall(msg)
                reply = curr_socket.recv(4096)
                if (reply == b"DONE"):
                        print("ho gya bro")
                        done[id] = True
                        active_clients -= 1
                        return
                if (msg == b"DONE"):
                    if len(reply>=3):
                        l=(reply[3:]).split(b'\n')[:-1]
                        for i in l:
                            curr_queue.put(lines[i])
                    curr_queue.put(b"DONE")
                elif (reply != b"OK"):
                    curr_queue.put(msg)
            except:
                curr_queue.put(msg)
        time.sleep(0.001)

def recv_from_client(id):
    #receives the messages from the client and handles them (puts in queue)
    global queues
    global clients_send
    global lines
    global lim
    global num_clients

    while len(lines) < lim:
        try:
            socket = clients_send[id]
            response=b''
            while True:
                response_new = socket.recv(4096)
                response+=response_new
                if(response_new[-1]==10):
                    socket.sendall(b"OK")
                    break
                if(response_new==b''):
                    break
            if(response[-1]!=10):
                continue
            index=0
            while (response[index]!=10):
                index+=1
            line_no=response[:index]
        except:
            continue
        if line_no not in lines:
            lines[line_no] = response
            logging.warning("client:"+str(len(lines)))
            for i in range(1,num_clients+1):
                if i != id:
                    queues[i].put(response)
    for i in range(1,num_clients+1):
        queues[i].put(b"DONE")
    clients_send[id].sendall(b"Done")

def get():
    global lines
    global lim
    global vayu_socket
    global vayucount
    global vayutime
    start = time.time()
    while (len(lines) < lim):
        curr = time.time()
        if (curr - start >= 0.001):
            count = 10
            old = start
            start = time.time()
            while(count >= 1):
                try:
                    vayu_socket.sendall(b"SENDLINE\n") 
                    break
                except:
                    count -= 1
                    continue
            if (count == 0):
                vayu_connect()
            else:
                response=b''
                while True:
                    response_new= vayu_socket.recv(4096)
                    response+=response_new
                    if response == b'-1\n\n':
                        start=old
                        break
                    if(response_new[-1]==10):
                        vayucount += 1
                        vayutime += curr-old
                        parse_thread=threading.Thread(target=parse,args=(response,))
                        parse_thread.start()
                        break
                    if(response_new==b''):
                        break
    submit()

def parse(data_string):
    global lines
    global num_clients
    global queues

    try:
        line_no=b""
        index=0
        while (data_string[index]!=10):
            index+=1
        line_no=data_string[:index]

        if line_no not in lines.keys():
            lines[line_no] = data_string
            for i in range(1,num_clients+1):
                queues[i].put(data_string)
            logging.warning("vayu"+str(len(lines)))
    except Exception as e:
        print("error: ", e)

def submit():
    global lines
    global vayu_socket
    global vayucount, vayutime
    global active_clients_recv
    global active_clients_send
    global done
    status=b'FAILED'
    for _ in range(10):
        if status == b"SUCCESS":
            break
        vayu_socket.sendall(b"SUBMIT\nKASHISH@COL334-672\n"+str(lim).encode('utf-8')+b"\n")
        for i in lines.values():
            vayu_socket.sendall(i)
        tempstatus = vayu_socket.recv(4096)
        status = tempstatus.split(b' ')[1]
    if(status==b"SUCCESS:"):
        print("SUCCESS",tempstatus)
    else:
        print("FAILED", tempstatus)
    print("active clients_send: ", active_clients_send )
    print("active_clients_recv: ", active_clients_recv)
    for u in done:
        print(u, done)
    print("vayu avg: ", vayutime/vayucount)
    vayu_socket.close()

def main():
    global num_clients
    global lim
    global active_clients_send
    global active_clients_recv
    global lines
    global done
    global queues
    global clients_send
    global clients_recv

    
    logging.warning("starting")
    logging.warning("num_clients: "+str(num_clients))
    recv_connect_threads={}
    send_connect_threads={}
    for i in range(1,num_clients+1):
        send_connect_threads[i]=threading.Thread(target=client_connect_send, args=(i,))
        recv_connect_threads[i]=threading.Thread(target=client_connect_recv, args=(i,))
        send_connect_threads[i].start()
        recv_connect_threads[i].start()
    while(active_clients_send<num_clients or active_clients_recv<num_clients):
        time.sleep(0.001)
    logging.warning("connected to all clients")
    vayu_connect()
    logging.warning("connected to vayu")

    send_threads={}
    recv_threads={}

    get_thread=threading.Thread(target=get)
    get_thread.start()

    for i in range(1,num_clients+1):
        send_threads[i]=threading.Thread(target=send_to_client, args=(i,))
        recv_threads[i]=threading.Thread(target=recv_from_client, args=(i,))
        send_threads[i].start()
        recv_threads[i].start()
        
    # while(len(lines)<lim):
    #     continue()

    for i in range(1,num_clients+1):
        send_threads[i].join()
        recv_threads[i].join()

    logging.warning("done")

if __name__ == "__main__":
    main()
