import socket
import threading

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

def main():
    server_ip = '10.184.3.218'  # Listen on all available interfaces
    port_1= 12345
    port_2= 12346
    port_3= 12347

    server_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket1.bind((server_ip, port_1))
    print("Server is listening for incoming connections...")
    server_socket1.listen(5)
    client_socket1, client_address1 = server_socket1.accept()
    server_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket2.bind((server_ip, port_2))
    server_socket2.listen(5)
    print("Server is listening for incoming connections...")
    # server_socket3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server_socket3.bind((server_ip, port_3))
    # server_socket3.listen(5)
    # print("Server is listening for incoming connections...")
    client_socket2, client_address2 = server_socket2.accept()
    # client_socket3, client_address3 = server_socket3.accept()

    client_thread1 = threading.Thread(target=handle_client, args=(client_socket1, client_address1))
    client_thread1.start()
    client_thread2 = threading.Thread(target=handle_client, args=(client_socket2, client_address2))
    client_thread2.start()
    # client_thread3 = threading.Thread(target=handle_client, args=(client_socket3, client_address3))
    # client_thread3.start()

if __name__ == "__main__":
    main()
