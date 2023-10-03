import socket
entry_id = "aseth@col334-672"
with open('output.txt', "r") as f:
    try:
        svayu = socket.socket()
        svayu.connect(("vayu.iitd.ac.in", 9801))
        lines = f.readlines()
        # Define the submission message
        submission_message = f"SUBMIT\n{entry_id}\n{len(lines)}\n"
        svayu.sendall(submission_message.encode())
        for line_number, line in enumerate(lines):
            submission_message = f"{line_number+1}\n{line}"
            svayu.sendall(submission_message.encode())

        # Send the submission message to the server

        # Receive and print the server's response
        response = svayu.recv(4096).decode('utf-8')
        print(response)

    except Exception as e:
        print("Error:", e)
    finally:
        svayu.close()
        
