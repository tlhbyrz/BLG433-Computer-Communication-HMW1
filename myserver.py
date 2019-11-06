from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from datetime import datetime
import random


class Server:
    def __init__(self, **kwargs):
        self.clients = {}  # Dictionary for client name
        self.addresses = {}  # Dictionary for client addresses
        self.names = {}
        self.games = []
        self.turnChecker = []
        self.turnHolder = 0
        self.word = "trivial"
        self.words = ['muscle', 'cat', 'board', 'body', 'love','telephone','computer','communication']
        self.current = "______________________________________"
        self.incorrectGuesses = []
        self.HOST = kwargs.get('host', '')
        self.PORT = kwargs.get('port', 12312)
        self.BUFFER_SIZE = 1024  # Buffer for one data fetch from the socket
        self.server = socket(AF_INET, SOCK_STREAM)  # TCP socket
        self.quit_message = "---quit---"
    
    def serve(self, number=5):
        self.server.bind((self.HOST, self.PORT))
        self.server.listen(number)

    def wait_connections(self):
        print("Waiting for connections...")

        while True:  # Infinitly listening new connections
            client, client_address = self.server.accept()  # A connection occured
            print(client, f'{client_address[1]} has connected')
            client.send(bytes("Welcome, please enter your username", "utf-8"))  # Welcome text
            self.addresses[client] = client_address  # Saving client adress
            Thread(target=self.communicate_client, args=(client,)).start()  # Infinitly wating messages from the client

    def communicate_client(self, client):  # Client listening function
        while True:
            name = client.recv(self.BUFFER_SIZE).decode("utf-8")  # Getting username from the client

            if name not in self.names:  # name is valid
                client.send(bytes(f'Welcome {name}, you can send messages now. For exit, plase type \'---quit---\'', "utf-8"))
                client.send(bytes("First word have " + str(len(self.word)) + " letter. Start guessing!", "utf-8"))
                self.broadcast(f'{name} has joined the game!')  # Announcing new client to everyone
                self.turnChecker.append(name)
                self.clients[client] = name  # Saving client name
                self.names[name] = True
                break
            else:  # name is not valid, ask for another one
                client.send(bytes(f'Username \'{name}\' is taken, please enter another one', "utf-8"))

        while True:  # Infinite loope for waiting messages of the client
            message = client.recv(self.BUFFER_SIZE).decode("utf-8")  # Wating a message
            message = message.lower()
            
            if name == self.turnChecker[self.turnHolder]:
                if self.turnHolder < (len(self.turnChecker) - 1):
                    self.turnHolder = self.turnHolder + 1
                else:
                    self.turnHolder = 0  

                if message != self.quit_message:  # Checking whether the client wants to leave the chat
                    if len(message) > 1:
                        if message == self.word:
                            self.broadcast(name + " completed the game. The guess is: " + message)
                            self.show_last_stuation()
                            self.game_over(name)
                        else:
                            self.incorrectGuesses.append(message)
                            self.broadcast(name + " made the wrong guess. The guess is: " + message) 
                            self.print_incorrect_guesses()   
                            self.show_last_stuation()     
                    else:
                        if message in self.word:
                            for i in range(len(self.word)):
                                if message == self.word[i]:
                                    self.current = self.current[0:i] + message + self.current[(i+1):]  
                            
                            if self.current[:len(self.word)] == self.word:
                                self.broadcast(name + " completed the game. The guess is: " + message)        
                                self.game_over(name)   
                            else:
                                self.broadcast(name + " made  correct guess. The guess is: " + message)   
                                self.show_last_stuation()      
                        else:
                            self.incorrectGuesses.append(message)
                            self.broadcast(name + " made the wrong guess. The guess is: " + message)    
                            self.print_incorrect_guesses() 
                            self.show_last_stuation()
                    
                    if len(self.incorrectGuesses) == 7:
                        self.game_over("no-winner","7 incorrect guess made in total.")

                    self.print_turn()     
                              
                else:
                    client.send(bytes("You are out of the chat room now :(", "utf-8"))
                    client.close()
                    del self.names[self.clients[client]]
                    del self.clients[client]  # Deleting client from the room
                    self.broadcast(f'{name} has left the chat.')
                    break  # Terminating the loop   
            else:
                pass       

    def print_turn(self):
        self.broadcast(self.turnChecker[self.turnHolder] + " has turn! ")            

    def show_last_stuation(self):
        self.broadcast("Last stuation: " + self.current[:len(self.word)])  
        self.broadcast("Incorrect guess: " + str(len(self.incorrectGuesses)))            

    def game_over(self, winner_name, message=""):
        self.games.append((winner_name,self.word))
        self.broadcast("Game is Over! " + message +  "The answer is : " + self.word)   
        self.print_games()
        self.recreate_game()

    def recreate_game(self):
        self.incorrectGuesses = []  
        self.current = "______________________________________"
        self.word = self.words[random.randint(0, 8) - 1]  
        self.broadcast("\n New word have " + str(len(self.word))  + " letter. Start guessing!" + ' \n' , False)

    def print_games(self):
        self.broadcast(". Game History: " , False)
        for game in self.games:
           self.broadcast("Winner: \'" + game[0] + "\' , Word: \'" + game[1] + '\' \n' , False)      

    def print_incorrect_guesses(self):
        self.broadcast("Incorrect Guess History: ")
        for guess in self.incorrectGuesses:
           self.broadcast("\'" + guess + "\', " , False)           

    def broadcast(self, message, show_time=True):
        for client in self.clients:  # Sending a message to all clients in the room
            if show_time:
                client.send(bytes(f"({datetime.now().strftime('%H:%M')}) " + message, "utf-8"))
            else:
                client.send(bytes(message, "utf-8"))    

    def close(self):
        self.server.close()


if __name__ == "__main__":
    host = '127.0.0.1'
    port = 12312


    client_limit = int(input("Enter a limit for client number (max = 5): "))
    
    if client_limit > 5:
        client_limit = 5
    elif client_limit < 0:
        client_limit = 1

    server = Server(host=host, port=port)
    server.serve(client_limit)
    connections = Thread(target=server.wait_connections())
    connections.start()  # Starts the infinite loop.
    connections.join()  # Waiting all thread to end to close the server
    server.close()