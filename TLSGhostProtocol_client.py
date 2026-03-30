
# 1. import libraries  

""" Socket defines an endpoint of a two-way communication between two or more programs, where inter-process communication (ICP) can take place
a socket is represented by the server's address combined with the port number"""
import socket 
# threading helps so that the client and server can be implemeted as two separate threads in one file rather than having to be run through different files
import threading
import struct # Packs the message length into bytes

# Define constants
Port = 4408
Message_Chunks_data_size = 40000


def send_msg(socket1, username):
    while True:
        message = input(f"{username}: ")
        if not message: continue

        if message.lower() in ["exit", "quit", "q", "e"]:
            print("Closing connection...")
            socket1.close()
            break # to exit the while loop

        # message with username data
        full_message = f"[{username}]: {message}".encode('utf-8')
        
        header = struct.pack('>Q', len(full_message))
        
        socket1.sendall(header + full_message)
    

def recv_msg(socket1, username):
    while True:
        try:

            header = socket1.recv(8)
            if not header: break
            
            msg_len = struct.unpack('>Q', header)[0]
            data = b""
            
            while len(data) < msg_len:
                remaining = msg_len - len(data)

                chunk = socket1.recv(min(remaining, Message_Chunks_data_size))
                if not chunk: break
                data += chunk
            
            print(f"\n{data.decode('utf-8')}\n{username}: ", end="")
            # print(f"\nReceiver: {data.decode('utf-8')}\nSender: ", end="")
        
        except Exception as e:
            print(f"\nConnection lost: {e}")
            break

def start_client():

    user = input("\nEnter your name or your device's name for this session: ")

    EC2_relay_server_ip = input("\nEnter the EC2 Relay Server IP: ")

    client_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_connection.connect((EC2_relay_server_ip, Port)) # Port will be implemented later
        print(f"\nConnected to the Relay Server at {EC2_relay_server_ip}")

        threading.Thread(target=recv_msg, args=(client_connection, user ), daemon=True).start()

        send_msg(client_connection, user)
    
    except Exception as e:
        print(f"\nCould not connect: {e}")

if __name__ == "__main__":
    try:
        start_client()
    except KeyboardInterrupt:
        print("\nUser exited with ^C, it is recommended to type exit, quit, q, or e to close the connection instead")