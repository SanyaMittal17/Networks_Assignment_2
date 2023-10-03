master_ip='10.194.39.113'
master_port=8000
vayu_ip='10.17.51.115'
vayu_port=9801
my_id=1

import socket
import threading
import logging
import time
from queue import Queue

global send_socket
global recv_socket
global vayu_socket

vayu_=(vayu_ip,vayu_port)

send_socket=None
recv_socket=None
vayu_socket=None

global lines
global recv_status
global vayucount
vayucount = 0
global vayutime
vayutime = 0
recv_status=False
lines={}
lim=1000
queue=Queue()

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
            time.sleep(0.01)
            continue

def client_connect(id,s):
    id_=bytes(str(id),'utf-8')+s
    port=master_port+id+ 1000*(s==b'#2')
    _socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _socket.connect((master_ip,port))
    _socket.sendall(id_)
    try:
        reply=_socket.recv(4096)
    except:
        reply=b''
    while(reply!=b"OK" and len(lines)<=lim):
        try:
            _socket.close()
        except:
            pass
        try:
            _socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            _socket.connect((master_ip,port))
            _socket.sendall(id_)
            reply=_socket.recv(4096)
        except:
            time.sleep(0.01)
            continue
    return _socket

def main():
    global send_socket
    global recv_socket
    global vayu_socket
    global my_id
    
    send_socket=client_connect(my_id,b'#1')
    recv_socket=client_connect(my_id,b'#2')

    vayu_connect()
    logging.warning("Connected to all sockets")
    
    # start threads
    get_thread=threading.Thread(target=get)
    get_thread.start()
    logging.warning("get thread started")
    recv_thread=threading.Thread(target=recv)
    recv_thread.start()
    logging.warning("recv thread started")
    send_thread=threading.Thread(target=send)
    send_thread.start()
    logging.warning("send thread started")

    # wait for threads to finish
    recv_thread.join()
    send_thread.join()
    # close sockets
    vayu_socket.close()
    send_socket.close()
    recv_socket.close()
    recv_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    send_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    recv_socket.connect((master_ip,master_port+my_id+1000))
    send_socket.connect((master_ip,master_port+my_id))
    recv_socket.close()
    send_socket.close()

def get():
    # get lines from vayu 
    global vayucount
    global vayutime
    start = time.time()
    while (len(lines) < lim):
        curr = time.time()
        #function which caters to the rate limit on vayu
        if (curr - start >= 0.001):
            count = 10
            #error handling for vayu socket connection
            old = start
            start = time.time()
            while(count >= 1):
                try:
                    vayu_socket.sendall(b"SENDLINE\n") 
                    break
                except:
                    count -= 1
                    continue
            #if error then create re-establish a new connection to vayu
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
    # lines: bit_string -> bit_string (line_no -> line)
    global lines
    # print("Parsing now", flush = True)
    try:
        line_no=b""
        index=0
        try:
            while (data_string[index]!=10):
                index+=1
        except:
            print("error:" , data_string[index])
            exit()
        line_no=data_string[:index]
        if line_no not in lines.keys() and len(lines)<lim:
            lines[line_no] = data_string
            logging.warning('vayu: ' + str(len(lines)))
            queue.put(data_string)
    except Exception as e:
        print("error: ", e)

def send():
    # this function is called in the parse function where you send a line you received from vayu to the master
    global send_socket
    global my_id
    global queue
    # for _ in range(10):
    #     try:
    #         send_socket.sendall(response)
    #         print("send completed")
    #         reply = send_socket.recv(4096)
    #         print("reply: ", reply)
    #         if reply == b"OK":
    #             return
    #     except Exception as e:
    #         print("error: ", e)
    #         continue
    # print("Not ended")
    # if(len(lines)<lim):
    #     client_connect(my_id,b'#1')
    #     send(response)
    reply=b''
    while(reply!=b'Done'):
        logging.warning("send thread waiting")
        reply=b''
        response=queue.get()
        for _ in range(10):
            try:
                send_socket.sendall(response)
                reply = send_socket.recv(4096)
                print("reply: ", reply)
                if reply == b"OK" or reply == b"Done":
                    break
            except Exception as e:
                print("error: ", e)
                continue
        if reply != b"OK" and reply != b"Done":
            client_connect(my_id,b'#1')
            queue.put(response)

            

def recv():
    # client stores the line in the local dictionary
    global lines
    global recv_status
    global recv_socket
    global lim
    global my_id
    # recv_socket.settimeout(2)
    while len(lines) <= lim:
        logging.warning("recv thread waiting")
        try:
            # print(len(lines))
            response=b''
            while True:
                response_new = recv_socket.recv(4096)
                response += response_new
                if response_new[-1]==10:
                    break
                if(response_new==b''):
                    break
            if(response[-1]!=10):
                continue
            try:
                if (response == b"DONE"):
                    if (len(lines) >= lim):
                        recv_socket.sendall(b"DONE")
                        break
                    else:
                        send_message = b"NO\n"
                        for i in range(0,lim):
                            encoded_key = str(i).encode()
                            if encoded_key not in lines.keys():
                                send_message += encoded_key + b"\n"
                        recv_socket.sendall(send_message)
                else:
                    line_no=b""
                    index=0
                    
                    while (response[index]!=10):
                        index+=1
                    line_no=response[:index]
                    if line_no not in lines.keys():
                        lines[line_no] = response
                        logging.warning('master: ' + str(len(lines)))
                    recv_socket.sendall(b"OK")
            except Exception as e:
                print("error1: ", e, response)
        except:
            client_connect(my_id,b'#2')
    # try:
    #     recv_socket.sendall(b"DONE")
    # except:
    #     pass
        
def submit():
    global lines
    global vayu_socket
    status=b'FAILED'
    for _ in range(10):
        if status == b"SUCCESS":
            break
        vayu_socket.sendall(b"SUBMIT\nKASHISH@COL334-672\n"+bytes(str(lim),'utf-8')+b"\n")
        for i in lines.values():
            vayu_socket.sendall(i)
        tempstatus = vayu_socket.recv(4096).split(b' ')
        status = tempstatus[1]
    if(status==b"SUCCESS:"):
        print("SUCCESS",tempstatus)
    else:
        print("FAILED",tempstatus)
    print("vayuavg: " , vayutime/vayucount)
    vayu_socket.close()

if __name__=="__main__":
    main()
