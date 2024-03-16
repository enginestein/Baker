# Baker

*Bot-Maker* Baker! Is a framework to create chatbots with Python in the easiest and simplest route, train your chatbot by texting or adding data in XML, JSON or YAML files. 

# Installation

You can install Baker with pip

```bash
pip install baker-python
```

# Usage

## Initial Tasks

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

The files can also be empty for example a JSON file can be like this:

```json
{

}
```

## Training

To train the chatbot, use the `Trainer` class. Here is an example of basic training:

```py
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
```

from this route the keyword (user's question) must be already created in the file or else the trainer will not be able to train because the trainer will not find the keyword in the file. For example if you want to train the chatbot for responses of `Hello` then `Hello` should be created in the data file.

But with this way to train you can train the chatbot as long you want to with custom keywords (no need to define them in the data file) and their infinite responses:

```py
import baker.trainer

trainer = baker.trainer.Trainer('data.json')
trainer.loop_training()
```

The data file can either be empty or it can have keywords, pre-defined keyowrds can be trained too.

# Parsing

To parse the chatbot to run and test it use the `Parser` class:

```py
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
```

The above code will run the chatbot, but there is anther simpler way to run the chatbot with it's specified name which is to use the `Chatbot` class:

```py
import baker.trainer
import baker.bparser
import baker.chatbot

trainer = baker.trainer.Trainer('data.json')
parser = baker.bparser.Parser('data.json')
my_chatbot = baker.chatbot.Chatbot("MyChatbot")
my_chatbot.session(trainer, parser)
```

`Parser` class has more functions regarding the data file:

- Exporting responses :

```py
import baker.bparser

response_file_name = "data.json"  
parser_instance = baker.bparser.Parser(response_file_name)  
parser_instance.export_responses(export_file_name="data2.json")
```

- Reset resposes

```py
baker.bparser.Parser.reset_responses("A_User_Question")
```

- Removing responses:

```py
parser_instance2 = baker.bparser.Parser("data.json")

user_input = "Hello"
response_to_remove = "Heyy"
parser_instance2.remove_response(user_input, response_to_remove)
```

- Count responses:

```py
parser_instance3 = baker.bparser.Parser("data.json")
user_input = "Hello"

count = parser_instance3.count_responses(user_input)
print(f"Number of Responses for '{user_input}': {count}")
```

Keep training your chatbot by texting or adding words in the database and then run it!