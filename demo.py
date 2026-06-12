from baker import Chatbot

bot = Chatbot("Baker", "data.json", backend='tfidf', memory=True)

bot.add_intent(
    "greeting",
    ["Hello", "Hi", "Hey", "Howdy", "Good morning", "Good evening"],
    ["Hey there!", "Hi {name}!", "Hello! How are you?"]
)
bot.add_intent(
    "farewell",
    ["Bye", "Goodbye", "See you later", "Talk later"],
    ["Goodbye {name}!", "See you later!", "Take care!"]
)

print("Baker Chatbot (ML backend: TF-IDF + char n-gram)")
print("New: Intents, Templates, Smart Response Selection")
print("=" * 50)
print("Examples:")
print("  Hello / Howdy / Good morning")
print("  My name is Alice")
print("  How are you / what is your name")
print("  Bye / Goodbye")
print("Commands: 'exit' to quit, 'teach' to train, 'stats' for context")

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    if user_input.lower() == "teach":
        print("Enter: question | response")
        while True:
            line = input("Teach: ")
            if line.lower() == "done":
                break
            if "|" in line:
                q, r = line.split("|", 1)
                bot.train(q.strip(), r.strip())
                print(f"  Learned: '{q.strip()}'")
        continue
    if user_input.lower() == "stats":
        ctx = bot.get_context()
        print(f"  Exchanges: {ctx.get('exchange_count', 0)}")
        print(f"  Entities: {ctx.get('entities', {})}")
        print(f"  Intents: {bot.list_intents()}")
        continue
    details = bot.respond_detailed(user_input)
    parts = [f"Bot: {details['response']}"]
    parts.append(f"(confidence: {details['confidence']})")
    if details.get('intents'):
        parts.append(f"intents: {details['intents']}")
    if details.get('entities'):
        parts.append(f"entities: {details['entities']}")
    print("  ".join(parts))
