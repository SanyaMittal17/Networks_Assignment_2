import socket
import multiprocessing

# Function to handle a client connection
def handle_client(client_socket, client_address):
    print("Connected by", client_address)

    while True:
        # Receive data from the client
        data = client_socket.recv(1024).decode('utf-8')
        if not data:
            break
        print("Received from", client_address, ":", data)

        # Send a response back to the client
        response = "Server received: " + data
        client_socket.sendall(response.encode('utf-8'))

    # Clean up the connection
    client_socket.close()
    print("Connection with", client_address, "closed")

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific address and port
server_address = '10.194.9.121'
ports=[12345,12346,12347,12348,12349]

i=ports[0]
server_socket.bind((server_address,i))
server_socket.listen(5)
print("Server is listening for incoming connections...")
while True:
# Accept a connection
    client_socket, client_address = server_socket.accept()
    print("Accepted a new connection from", client_address)
    # a new process to handle the client connection
    handle_client(client_socket, client_address)





# # first of all import the socket library
# import socket			

# # next create a socket object
# s = socket.socket()		
# print ("Socket successfully created")

# # reserve a port on your computer in our
# # case it is 12345 but it can be anything
# port = 12345			

# # Next bind to the port
# # we have not typed any ip in the ip field
# # instead we have inputted an empty string
# # this makes the server listen to requests
# # coming from other computers on the network
# s.bind(('10.194.9.121', port))		
# print ("socket binded to %s" %(port))

# # put the socket into listening mode
# s.listen(5)	
# print ("socket is listening")		

# # a forever loop until we interrupt it or
# # an error occurs
# while True:

# # Establish connection with client.
#     c, addr = s.accept()	
#     print ('Got connection from', addr )

#     data=c.recv(1024).decode()
#     print("Received from", addr, ":", data)
#     # send a thank you message to the client. encoding to send byte type.
#     c.send(f'{data}, Thank you for connecting'.encode())

#     # Close the connection with the client
#     c.close()
