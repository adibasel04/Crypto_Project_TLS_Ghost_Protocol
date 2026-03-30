
# Chat application implementing the TLS Ghost Protocol 

# TCP is being implemented since it is more reliable and guarantees that each message (packet) reaches to a receiver from the sender in the order that the packets were sent

# 1. import libraries  

""" Socket defines an endpoint of a two-way communication between two or more programs, where inter-process communication (ICP) can take place
a socket is represented by the server's address combined with the port number"""
import socket 
# threading helps so that the client and server can be implemeted as two separate threads in one file rather than having to be run through different files
import threading
import struct # Packs the message length into bytes

# Define constant variables
Port = 4408
clients = []

def broadcast(message, sender_socket):

    for client in clients:
        """ Sends all clients the message except for the sender themselves **fix this to be for specified client to specified client instead of all clients"""
        if client != sender_socket:
            try:
                client.sendall(message)
            except:
                # When the except statement is executed it could specify that sending failed, which implies that client might have disconnected
                clients.remove(client) 

def handle_client(conn, addr):

    # Individual thread to manage each person who connects 
    print(f"\n[New Connection] {addr} connected")

    while True:
        try:

            header = conn.recv(8)
            if not header:
                break

            message_len = struct.unpack(">Q", header)[0]
            data = b""
            while len(data) < message_len:
                messageblock = conn.recv(min((message_len - len(data)), 40000))
                if not messageblock:
                    break
                data += messageblock
            
            broadcast(header + data, conn)

        except Exception as e:
            print(f"\n[ERROR] Connection with {addr} closed: {e}")
            break
    
    conn.close()
    if conn in clients:
        clients.remove(conn)


def start_server():
    
    """ The family domain for this server socket is AF_INET which defines connection through IP and SOCK_STREAM refers to using TCP for the communication
    since SOCK_DGRAM refers to datagrams which are packets used by UDP that do not confirm a packet was received (fire and forget) """
    server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    
    # Bind to '0.0.0.0' so it listens to any device on the public network 
    server_connection.bind(('0.0.0.0', Port)) # Port will be implemented later
    server_connection.listen(10) # Backlog of 10
    print(f"\nEC2 Relay Server online. Waiting for client to connect ...")

    while True:  
        conn, addr = server_connection.accept()
        print(f"Connected to client {addr}")
        clients.append(conn)
                
        # Start the threads!
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
