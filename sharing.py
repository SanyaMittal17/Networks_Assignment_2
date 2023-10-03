import socket
from time import sleep
def main():
    host = 'vayu.iitd.ac.in'
    port = 9801
    text=[None]*1000
    found=0
    tries=0
    no=0
    ind=-1
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        print(f"Connected to {host}:{port}")
        while(found<1000):
            tries+=1
            response=sock.sendall(b"SENDLINE\n")   
            response = sock.recv(4096)  
            decoded_response = response.decode().split("\n")  # Convert the bytes to a string
            try:
                p=ind
                ind=int(decoded_response[0])
                if(ind<0):
                    no+=1
                    ind=p
                    continue
                if(text[ind]==None):
                    text[ind]=decoded_response[1]
                    found+=1
                sleep(0.001)
            except Exception as e:
                text[ind]+=decoded_response[0]
                print(found)
                sleep(0.003)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        sock.close()
        print("Connection closed")
        # print("\n".join(text))
        print(no)
        # print(m)

if __name__ == "__main__":
    main()
