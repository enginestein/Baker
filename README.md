# Baker

*Bot-Maker* Baker! Is a framework to create chatbots with Python in the easiest and simplest route, train your chatbot by texting or adding data in XML, JSON or YAML files. 

# Installation

You can install Baker with pip

```bash
pip install baker-python
```

# Usage

Using Baker is very easy, all you have to do is to create a YAML, JSON or XML file first. However, files should have been defined in a specific format:

**For XML files**

```xml
<responses>
  <Hello>
    <response>Hello!</response>
    <response>Hi there!</response>
  </Hello>
</responses>
```

The `Hello` tag is defining that if the user will write `Hello` to the chatbot the chatbot will return one of the responses in the `response` tag.

**For JSON files**

```json
{
    "Hello": [
        "Hi",
        "Heyy",
        "Hello"
    ]

}
```

Same goes with JSON files. Even if the response is only one, it must be in a list []. Here, if user inputs `Hello` then the response must be random in the list. 

**For YAML files**

```yaml
Hello:
- Hello!
- Hi there!
How are you:
- I am fine
- I am doing good, thanks for asking
```

Same process is with the YAML files with a bit different syntax and nothing else.

To train the chatbot, the `Trainer` class is used:

```py
bot = Trainer('database.yaml')

user_input = input("You: ")
response = bot.get_response(user_input)
print("Bot:", response)

# Train the bot with a new response
new_response = input("New response: ")
bot.train_response(user_input, new_response)
print("Bot has been trained with the new response!")
```

Note :- The keyword must be already created in the file or else the trainer will not be able to train because the trainer will not find the keyword in the file. For example if you want to train the chatbot for responses of `Hello` then `Hello` should be at least created in the data file. 

To parse the chatbot use the `Parser` class:

```py
def test_chatbot(bot):
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Testing session ended.")
            break
        response = bot.get_response(user_input)
        print("Bot:", response)

bot = Parser('database.json')

test_chatbot(bot)
```

The above code will run the chatbot, but there is anther simpler way to run the chatbot with it's specified name which is to use the `Chatbot` class:

```py
trainer = Trainer('database.json')
parser = Parser('database.json')
my_chatbot = Chatbot("MyChatbot")
my_chatbot.interactive_session(trainer, parser)
```

Keep training your chatbot by texting or adding words in the database and then run it!
