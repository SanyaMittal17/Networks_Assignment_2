import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the remote server's IP address and port
server_address = ('10.194.9.121', 12345)  # Replace 'remote_server_ip' with the actual IP or hostname
print("Connecting to", server_address)
client_socket.connect(server_address)
print("Connected!")

while True:
    message = input("Enter a message to send: ")
    if message.lower() == 'exit':
        break

    client_socket.sendall(message.encode('utf-8'))
    response = client_socket.recv(1024).decode('utf-8')
    print("Server response:", response)

client_socket.close()



# # Import socket module
# import socket			

# # Create a socket object
# s = socket.socket()		

# # Define the port on which you want to connect
# port = 12345			

# # connect to the server on local computer
# s.connect(('10.194.9.121', port))
# name=input("Enter your name: ")
# s.send(name.encode())

# # receive data from the server and decoding to get the string.
# print (s.recv(1024).decode())
# # close the connection
# s.close()	
	
