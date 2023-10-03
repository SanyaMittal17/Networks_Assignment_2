import socket		
import logging	
import json
from time import sleep
s = socket.socket()	
port = 8001			
s.connect(("10.194.13.44", port))
print("connected")
def main():
    global s
    svayu = socket.socket()
    reply = s.recv(4096).decode('utf-8')
    while reply != "OK":
        reply = s.recv(4096).decode('utf-8')

    svayu.connect(("10.17.7.134", 9801))
    svayu.sendall(b"SESSION RESET\n")
    reply1=svayu.recv(4096).decode('utf-8')
    while True:
        try:
            svayu.sendall(b"SENDLINE\n")
            response = svayu.recv(4096).decode('utf-8')
            if(response=="-1\n-1\n"):
                continue
            reply=sendline(response)
            logging.warning(reply)
            if (reply=="1"):
                # received_data_json = s.recv(1024).decode()
                # received_data = json.loads(received_data_json)
                # print(received_data)
                s.close()
                break
        except Exception as e:
            print("error: ", e)
            svayu.close()
            break
    print("Done")
    s.close()
    svayu.close()
def sendline(sendtext):
    global s
    echo = None
    while (echo != '0'):
        try:
            s.send(sendtext.encode())
            echo =  s.recv(1024).decode()
            if (echo=="1"):
                s.close()
                break
        except:
            print("error")
    return echo
if __name__ == "__main__":
    main()
