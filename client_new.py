import socket		
import logging	
from time import sleep
from multiprocess import Process, Value
s = socket.socket()	
port = 8001
master="10.194.1.207"		
s.connect((master, port))
s2=socket.socket()
port2=port+1000
s2.connect((master,port2))
reply_done=Value('i',0)
def check_done():
    while True:
        r=s2.recv(4096)
        logging.warning(r.decode('utf-8'))
        if(r==b'1'):
            s2.sendall(b'1')
            break
    reply_done.value=1
    s2.close()
def main():
    global s
    svayu = socket.socket()
    reply = s.recv(4096)
    while reply != b"OK":
        reply = s.recv(4096)
    reply = s2.recv(4096)
    while reply != b"OK":
        reply = s.recv(4096)
    done_thread=Process(target=check_done)
    done_thread.start()
    svayu.connect(("10.17.51.115", 9801))
    svayu.sendall(b"SESSION RESET\n")
    reply1=svayu.recv(4096)
    while reply_done.value!=1:
        try:
            svayu.sendall(b"SENDLINE\n")
            response=b''
            while True:
                response_new= svayu.recv(4096)
                response+=response_new
                if(response_new==b'' or response_new[-1]==10):
                    break
            if(response==b"-1\n-1\n"):
                continue
            try:
                s.sendall(response)
                logging.warning(response)
            except:
                print("error")
        except Exception as e:
            print("error: ", e)
            svayu.close()
            break
    svayu.close()
    print("Done")
    s.close()
if __name__ == "__main__":
    main()
