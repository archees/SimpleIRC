import socket
import threading
import sys

username = input("Enter your full name: ")
threads = []
FORMAT = 'utf-8'
#To connect to the server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))
# To start communication between server and client
# The message will be decoded when recived by the client
#This function is to get message from the server

def get_message():
  connected = True
  while connected:
        try:
            message = client.recv(2048)
            raw_message = message.decode(FORMAT)
            if raw_message == 'QUIT':
              sys.exit(0)

            if raw_message == 'NICK':
                client.send(username.encode(FORMAT))
            else:
                print(raw_message)
        except Exception as e:
            client.close()
            sys.exit(2)
# This function is to send the message to the server
#The message will get encoded when sent to server

def send_message():
  connected = True
  while connected:
        message = '{} {}'.format(username, input(''))
        try:
            client.send(message.encode('utf-8'))
        except:
            client.close()
            sys.exit(0)
#This function is used to start the chat system between server and client
#Threading is used to communicate with multiple clients

def start_chat():
    get_message_thread = threading.Thread(target=get_message)
    get_message_thread.start()
    threads.append(get_message_thread)
    send_message_thread = threading.Thread(target=send_message)
    send_message_thread.start()
    threads.append(send_message_thread)
start_chat()

