#test-chatbot.py

import baker.trainer
import baker.bparser
import baker.chatbot

trainer = baker.trainer.Trainer('data.json')
parser = baker.bparser.Parser('data.json')
my_chatbot = baker.chatbot.Chatbot("MyChatbot")
my_chatbot.session(trainer, parser)

#test-functions.py

import baker.bparser

response_file_name = "data.json"  
parser_instance = baker.bparser.Parser(response_file_name)  
parser_instance.export_responses(export_file_name="data2.json")

baker.bparser.Parser.reset_responses("A_User_Question")


parser_instance2 = baker.bparser.Parser("data.json")

user_input = "Hello"
response_to_remove = "Heyy"
parser_instance2.remove_response(user_input, response_to_remove)

parser_instance3 = baker.bparser.Parser("data.json")
user_input = "Hello"

count = parser_instance3.count_responses(user_input)
print(f"Number of Responses for '{user_input}': {count}")

#test-loop-trainer.py

import baker.trainer

trainer = baker.trainer.Trainer('data.json')
trainer.loop_training()

#test-parser.py

import baker.bparser

def test_chatbot(bot):
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Testing session ended.")
            break
        response = bot.get_response(user_input)
        print("Bot:", response)

bot = baker.bparser.Parser('data.json')

test_chatbot(bot)

#test-trainer.py

import baker.trainer
import baker.bparser
import baker.chatbot

bot = baker.trainer.Trainer('data.json')

user_input = input("You: ")
response = bot.get_response(user_input)
print("Bot:", response)

# Train the bot with a new response
new_response = input("New response: ")
bot.train_response(user_input, new_response)
print("Bot has been trained with the new response!")