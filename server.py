#The socket module is imported to createe and communicate through sockets
#thread is used for multithreading for multiple clients
import socket
import threading 


host = '127.0.0.1' #IP address of the localhost
port = 55555  #Using unreserved port numbers
FORMAT ='utf-8' #encoding format used to send and recieve messages

#Creating server socket
#AF_INET is for the type of addresses that makes connection (Internet) and SOCK_STREAM is for tcp connections
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))#binding the socket to the host and port numbers
server.listen() #The server starts listening 

#the commands are displayed for the user after connecting to the server               
Command='\nList of commands:\n' \
		'1.$list --> list of rooms and roomdetails\n' \
		'2.$join roomname --> join or create the room\n' \
		'3.$switch roomname -->switch rooms\n' \
		'4.$personal -->To send personal message\n' \
		'5.$leave --> leave the room\n' \
		'6.$quit -->to log off\n' \
		'7.$help --> list all the commands\n' \

#dictionary and list created to store client and room details
Ip_Client = []
Nick_Names = []
R_Details = {}
Account = {}
Room_Users = {}


#User class to store user details
class User:
    def __init__(self, Name):
        self.Name = Name
        self.R_Details = []
        self.Current_Room = ''

#room class is used to store room details
class Room:
    def __init__(self, Name):
        self.Members = []
        self.Nick_Names = []
        self.Name = Name


#this function is used to broadcast a message in the room
def Broadcast(Message, Room_name, Nick_Name):
	user = Room_Users[Nick_Name]
	if user.Current_Room == Room_name:
		for client in R_Details[Room_name].Members:
			msg = f'[{Room_name}] {Message}'
			client.send(msg.encode(FORMAT))

#function to list all the rooms and the users in the rooms
def R_Details_Record(Nick_Name):
    Name = Account[Nick_Name]
    print(len(R_Details))
    if len(R_Details) == 0:
        Name.send('No roomdetails are available to join'.encode('FORMAT'))
    else:
        Reply = "List of available roomdetails: \n"
        for room in R_Details:
            Room_dtl = R_Details[room]
            print(Room_dtl.Name)
            Reply += Room_dtl.Name
            print(Room_dtl.Nick_Names)

            #if nickname not in roomdetails[room].nicknames:
            for Members in R_Details[room].Nick_Names:
                Reply += Members + '\n'
        Name.send(f'{Reply}'.encode(FORMAT))


#This function is used to join client to a room
def Room_Join(Nick_Name, Room_Name):
	Name = Account[Nick_Name]
	user = Room_Users[Nick_Name]
	if Room_Name not in R_Details:
		room = Room(Room_Name)
		R_Details[Room_Name] = room
		room.Members.append(Name)
		room.Nick_Names.append(Nick_Name)
		user.Current_Room = Room_Name
		user.R_Details.append(room)
		Name.send(f'{Room_Name} Created'.encode(FORMAT))
	else:
		room = R_Details[Room_Name]
		if Room_Name in user.R_Details:
			Name.send('You are in the room already!'.encode(FORMAT))
		else:
			room.Members.append(Name)
			room.Nick_Names.append(Nick_Name)
			user.Current_Room = Room_Name
			user.R_Details.append(room)
			Broadcast(f'{Nick_Name} Entered the Room', Room_Name, Nick_Name)
       

        

#This function is used to switch room from current to requested room
def switch_room(Nick_Name, Room_Name):
	user = Room_Users[Nick_Name]
	Name = Account[Nick_Name]
	room = R_Details[Room_Name]
	try:
		if Room_Name == user.Current_Room:
			Name.send('You are in the room already!'.encode(FORMAT))
		elif room not in user.R_Details:
			Name.send('You are not in the Room so,Unable to switch the Room'.encode(FORMAT))
		else:
			user.Current_Room = Room_Name
			Name.send(f'Switched to {Room_Name}'.encode(FORMAT))
	except Exception as e:
		print("exception occured", e)

#This function is defined for client leaving a room
def Leave_Room(Nick_Name):
	user = Room_Users[Nick_Name]
	Name = Account[Nick_Name]
	if user.Current_Room == '':
		Name.send('You are not in any Room'.encode(FORMAT))
	else:
		Exit_Room(user, Name, Nick_Name) #calling the exit room if there exists roomname


#exit the room function definition
def Exit_Room(user, Name, Nick_Name):
	Room_Name = user.Current_Room
	room = R_Details[Room_Name]
	user.Current_Room = ''
	user.R_Details.remove(room)
	room.Members.remove(Name)
	room.Nick_Names.remove(Nick_Name)
	Broadcast(f'{Nick_Name} Exit the room', Room_Name,Nick_Name)
	Name.send('You Exited the room'.encode(FORMAT))


#Function defined for private messaging feature
def Personal_Msg(Message):
    args = Message.split(" ")
    user = args[2]
    sender = Account[args[0]]
    if user not in Account:
        sender.send('Unable to locate the user'.encode(FORMAT))
    else:
        reciever = Account[user]
        msg = ' '.join(args[3:])
        reciever.send(f'[personal message] {args[0]}: {msg}'.encode(FORMAT))
        sender.send(f'[personal message] {args[0]}: {msg}'.encode(FORMAT))

#feature for client exiting the server
def Remove_Client(Nick_Name):
	Nick_Names.remove(Nick_Name)
	Client = Account[Nick_Name]
	user = Room_Users[Nick_Name]
	user.Current_Room = ''
	for room in user.R_Details:
		Server_Exit(room, Client, Nick_Name)


#Feature for server exiting message
def Server_Exit(room, Client, Nick_Name):
	print(room.Name)
	room.Members.remove(Client)
	print(room.Members)
	room.Nick_Names.remove(Nick_Name)
	print(room.Nick_Names)
	Broadcast(f'{Nick_Name} Exited the Room', room.Name,Nick_Name)

#function defined to give details of the commands
def help(Nick_Name,command):
	Name = Account[Nick_Name]
	if command is None:
		Name.send(Command.encode(FORMAT))
	else:
		if command == 'list':
			Name.send('\nCommand: $list\n'.encode(FORMAT))
			Name.send('Arguments: none\n'.encode(FORMAT))
			Name.send('Description: The list of rooms on server and thier details are displayed\n'.encode(FORMAT))

		elif command == 'join':
			Name.send('\nCommand: $join\n'.encode(FORMAT))
			Name.send('Arguments: <roomname> \n'.encode(FORMAT))
			Name.send('Description: The command will allow you to join the room specified\n'.encode(FORMAT))
			Name.send('when roomname that is not on the list is given, it will create a new room\n'.encode(FORMAT))

		elif command == 'quit':
			Name.send('\nCommand: $exit\n'.encode(FORMAT))
			Name.send('Arguments: none\n'.encode(FORMAT))
			Name.send('Description: The quit command will log you off the server\r\n'.encode(FORMAT))

		elif command == 'leave':
			Name.send('\nCommand: $leave\n'.encode(FORMAT))
			Name.send('Arguments: <channel> (required)\n'.encode(FORMAT))
			Name.send('Description: The leave command will take you out of the channel specified by <channel>\n'.encode(FORMAT))
			Name.send('You must be in a channel in order to leave it.\n'.encode(FORMAT))
          
		elif command == 'switch':
			Name.send('\nCommand: $switch\n'.encode(FORMAT))
			Name.send('Arguments: <channel> (required)\n'.encode(FORMAT))
			Name.send('Description: The current command will switch your current room \n'.encode(FORMAT))
			Name.send('You must be in the channel specified by <channel>\n'.encode(FORMAT))
            

		elif command == 'personal':
			Name.send('\nCommand: $personal\n'.encode(FORMAT))
			Name.send('Arguments: <user>, <message> (required)\n'.encode(FORMAT))
			Name.send('Description: Send private message <message> to <user>\n'.encode(FORMAT))

		else:
			Name.send('\nSpecified command does not exist.'.encode(FORMAT))
			Name.send(' Type $help <command> for list of commands\r\n'.encode(FORMAT))

#The target function of thread to analyse the client requests
def handle(Client):
    connected = True
    nick=''
    while connected:
        try:
            Message = Client.recv(1024).decode(FORMAT)
            args = Message.split(" ")
            Name = Account[args[0]]
            nick = args[0]
            Commands(nick, Message, args, Name)
        except Exception as e:
            #print("exception occured:", e)
            index = Ip_Client.index(Client)
            Ip_Client.remove(Client)
            Client.close()
            print(f'Nick_name is {nick}')
            
            if nick in Nick_Names:
                Remove_Client(nick)
                Nick_Names.remove(nick)
            break
            #if nick in nicknames:
                #nicknames.remove(nick)
                #break
#function definition for response for analyzed messages
def Commands(nick, Message, args, Name):
    if '$help' in Message:
        help(args[0], ' '.join(args[2:]))
    elif '$list' in Message:
        R_Details_Record(args[0])
    elif '$join' in Message:
        Room_Join(args[0], ' '.join(args[2:]))
    elif '$leave' in Message:
        Leave_Room(args[0])
    elif '$personal' in Message:
        Personal_Msg(Message)
    elif '$switch' in Message:
        switch_room(args[0],' '.join(args[2:]))
    elif '$quit' in Message:
        Remove_Client(args[0])
        Name.send('QUIT'.encode(FORMAT)).close()
    elif Room_Users[args[0]].Current_Room == '':
        Name.send('You do not belong to any of the rooms'.encode(FORMAT))
    else:
        msg = ' '.join(args[1:])
        Broadcast(f'{args[0]}: {msg}',Room_Users[args[0]].Current_Room,nick)
#function definition to recieve client responses
def recieve():
    connected = True
    while connected:
        Client, Address = server.accept()
        print(f'Connected to {str(Address)}', Client)
        #print(client)
        Client.send('NICK'.encode(FORMAT))
        Nick_Name = Client.recv(1024).decode(FORMAT)
        Nick_Names.append(Nick_Name)
        Ip_Client.append(Client)
        user = User(Nick_Name)
        Room_Users[Nick_Name] = user
        Account[Nick_Name] = Client
        print(f'Client Name is: {Nick_Name}')
        #broadcast(f'{nickname} joined the chat'.encode('utf-8'))
        Client.send('Server Connected!!'.encode(FORMAT))
        Client.send(Command.encode(FORMAT))
        thread = threading.Thread(target=handle, args=(Client,)).start()
        #thread.start()

print('Server Started!!')
recieve()



