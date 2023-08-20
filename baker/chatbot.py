import re
from parser import Parser
from trainer import Trainer

class Chatbot:
    def __init__(self, name):
        self.name = name
        
    def session(self, trainer, parser):
        print(f"Welcome to {self.name} Chatbot! Type 'exit' to end the session.")
        while True:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                print("Session ended.")
                break
            response = parser.get_response(user_input)
            print("Bot:", response)