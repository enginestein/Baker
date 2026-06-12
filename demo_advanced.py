from baker import Chatbot
import json

TEST_QUERIES = [
    ("greetings", [
        "Hello",
        "hi there",
        "good morning",
        "howdy partner",
        "hey how are you doing",
    ]),
    ("farewells", [
        "bye",
        "goodbye",
        "see you later",
        "catch you later",
    ]),
    ("identify + typos", [
        "who r u",
        "whats your name",
        "who made you",
        "what can you do",
    ]),
    ("science & space", [
        "tell me about black holes",
        "what is gravity",
        "how do rockets work",
        "is there life on mars",
        "will the sun explode",
    ]),
    ("technology", [
        "what is python",
        "how do computers work",
        "what is machine learning",
        "what is a database",
        "what is the internet",
    ]),
    ("history & people", [
        "who was albert einstein",
        "tell me about the roman empire",
        "what happened in world war 2",
        "who painted the mona lisa",
    ]),
    ("food & cooking", [
        "how do i cook pasta",
        "how do i make pizza",
        "what should i eat today",
        "how do i make coffee",
    ]),
    ("health & mindset", [
        "how do i reduce stress",
        "i feel sad",
        "i am bored",
        "what is mindfulness",
        "how do i sleep better",
    ]),
    ("nature", [
        "how deep is the ocean",
        "what is the largest animal",
        "how do bees make honey",
        "tell me about dinosaurs",
        "what is the fastest animal",
    ]),
    ("philosophy", [
        "what is the meaning of life",
        "what happens after death",
        "what is consciousness",
        "are you sentient",
    ]),
    ("mischief — typos & fragments", [
        "helloo",
        "phithon programing",
        "blak hole",
        "gravy",
        "cooking pasta",
        "rocket",
    ]),
    ("mischief — close but wrong", [
        "what's the whether like",
        "can you cook",              # close to "How do I cook pasta" and "Tell me about cooking"
        "aint nobody got time for dat",
        "tell me a fun fact",
    ]),
]

bot = Chatbot(
    "Baker",
    "knowledge_base.json",
    backend='tfidf',
    memory=True,
    threshold=0.25,
    intent_threshold=0.2,
)

bot.add_intent(
    "greeting",
    ["Hello", "Hi", "Hey", "Howdy", "Good morning", "Good afternoon", "Good evening", "Hey there", "What's up"],
    ["Hey {name}! Great to see you!", "Hello! How can I help you today?", "Hi there! Ready to chat about anything?", "Hey! What's on your mind?"],
)
bot.add_intent(
    "farewell",
    ["Bye", "Goodbye", "See you later", "Take care", "Catch you later", "Talk to you later"],
    ["Goodbye {name}! Come back anytime!", "See you later! Take care.", "Bye! It was great chatting with you."],
)
bot.add_intent(
    "thanks",
    ["Thank you", "Thanks", "Thanks a lot", "Thank you so much", "Appreciate it", "Thanks for your help"],
    ["You're very welcome {name}!", "My pleasure! Always happy to help.", "Anytime! That's what I'm here for."],
)
bot.add_intent(
    "mood_good",
    ["I am happy", "I'm great", "I feel good", "I'm doing well", "I am fine", "feeling good"],
    ["That's wonderful {name}! What's making you feel good today?", "I'm glad to hear that! Happiness looks good on you!", "Awesome! Hold onto that feeling and share it with others!"],
)
bot.add_intent(
    "mood_bad",
    ["I feel sad", "I'm not good", "I am depressed", "I feel terrible", "I'm having a bad day", "feeling down"],
    ["I'm sorry you're feeling that way, {name}. I'm here for you. Want to talk about it?", "That sounds really tough. Remember that feelings are temporary. Is there anything I can help with?", "I hear you. Sometimes just talking about it helps. What's going on?"],
)
bot.add_intent(
    "joke",
    ["Tell me a joke", "Tell me another joke", "Do you know any jokes", "Make me laugh", "Tell me something funny"],
    ["Here's one: Why don't scientists trust atoms? Because they make up everything!", "What do you call a bear with no teeth? A gummy bear!", "Why did the scarecrow win an award? He was outstanding in his field!"],
    negative_examples=["tell me about", "explain", "what is", "how do", "who is", "tell me something about"],
)
bot.add_intent(
    "compliment",
    ["You are great", "You are smart", "I like you", "You are amazing", "You're the best", "Good bot"],
    ["Thanks {name}! You're pretty amazing yourself!", "I appreciate that! I try my best with my little vector space!", "Aww shucks! You're making my circuits blush!"],
    negative_examples=["you are not", "you aren't", "you're not", "you are terrible", "you are bad", "you are dumb", "you are stupid", "you are wrong"],
)

BOLD = "\033[1m"
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
DIM = "\033[2m"


def color_conf(conf):
    if conf >= 0.8:
        return f"{GREEN}{conf}{RESET}"
    elif conf >= 0.5:
        return f"{YELLOW}{conf}{RESET}"
    else:
        return f"{RED}{conf}{RESET}"


def interactive_mode():
    print(f"\n{BOLD}{CYAN}╔══════════════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║        Baker Advanced Demo — Interactive Mode         ║{RESET}")
    print(f"{BOLD}{CYAN}╚══════════════════════════════════════════════════════╝{RESET}")
    print(f"{DIM}Knowledge base: 208 entries, 633 responses{RESET}")
    print(f"{DIM}Intents: greeting, farewell, thanks, mood_good, mood_bad, joke, compliment{RESET}")
    print(f"{DIM}Backend: TF-IDF + char n-gram | Threshold: 0.25{RESET}")
    print()
    print(f"{YELLOW}Commands:{RESET}")
    print(f"  {BOLD}test{RESET}     Run the full test suite of {sum(len(q[1]) for q in TEST_QUERIES)} queries")
    print(f"  {BOLD}stats{RESET}    Show conversation stats")
    print(f"  {BOLD}intents{RESET}  List registered intents")
    print(f"  {BOLD}teach{RESET}    Train a new response (format: question | response)")
    print(f"  {BOLD}sessions{RESET} Show conversation history")
    print(f"  {BOLD}exit{RESET}     Quit")
    print()

    while True:
        user_input = input(f"{BOLD}You:{RESET} ").strip()
        if not user_input:
            continue
        if user_input.lower() == "exit":
            break
        if user_input.lower() == "test":
            run_test_suite()
            continue
        if user_input.lower() == "stats":
            ctx = bot.get_context()
            print(f"  Exchanges: {ctx.get('exchange_count', 0)}")
            print(f"  Entities: {ctx.get('entities', {})}")
            print(f"  Topics discussed: {len(ctx.get('topics', []))}")
            continue
        if user_input.lower() == "intents":
            print(f"  Intents: {bot.list_intents()}")
            continue
        if user_input.lower() == "sessions":
            mem = bot.get_context()
            history = mem.get('history', []) if isinstance(mem, dict) else []
            print(f"  History ({len(history)} exchanges):")
            for i, (q, r) in enumerate(history[-10:], 1):
                print(f"    {i}. {DIM}{q[:50]}{RESET} → {r[:60]}")
            continue
        if user_input.lower() == "teach":
            print("Enter: question | response")
            while True:
                line = input("Teach: ").strip()
                if line.lower() == "done":
                    break
                if "|" in line:
                    q, r = line.split("|", 1)
                    bot.train(q.strip(), r.strip())
                    print(f"  Learned: '{q.strip()}'")
                else:
                    print("  Use: question | response")
            continue

        respond_and_show(user_input)


def respond_and_show(query):
    details = bot.respond_detailed(query)

    print(f"{DIM}  ── response ──────────────────────────────────────────{RESET}")
    print(f"  {BOT_COLOR or BOLD}{details['response']}{RESET}")

    conf = details['confidence']
    if isinstance(conf, float):
        print(f"  {DIM}confidence:{RESET} {color_conf(conf)}", end="")
    if details.get('matched_key'):
        print(f"  {DIM}matched key:{RESET} {CYAN}{details['matched_key']}{RESET}", end="")
    print()

    if details.get('intents'):
        print(f"  {DIM}intents:{RESET} {details['intents']}")
    if details.get('entities'):
        print(f"  {DIM}entities:{RESET} {details['entities']}")
    if details.get('sentiment') and details['sentiment'] != 'neutral':
        print(f"  {DIM}sentiment:{RESET} {details['sentiment']}")

BOT_COLOR = CYAN


def run_test_suite():
    total = sum(len(q[1]) for q in TEST_QUERIES)
    passed = 0
    failed = 0

    bot.memory = None

    print(f"\n{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD}Running {total} test queries across {len(TEST_QUERIES)} categories{RESET}")
    print(f"{BOLD}{'=' * 60}{RESET}\n")

    for category, queries in TEST_QUERIES:
        print(f"{BOLD}{YELLOW}▸ {category.upper()}{RESET}")
        for q in queries:
            details = bot.respond_detailed(q)

            response = details['response']
            conf = details['confidence']
            has_response = isinstance(response, str) and len(response) > 5
            has_confidence = isinstance(conf, float) and conf >= 0.0

            status = f"{GREEN}✓{RESET}" if has_response else f"{RED}✗{RESET}"
            if has_response:
                passed += 1
            else:
                failed += 1

            print(f"  {status} {DIM}{q:<40}{RESET} ", end="")
            trunc = response[:55] + "..." if len(response) > 55 else response
            print(f"{BOLD}{trunc}{RESET}  ", end="")
            print(f"{DIM}[{color_conf(conf)}]{RESET}")

        print()

    print(f"{BOLD}{'=' * 60}{RESET}")
    print(f"Results: {GREEN}{passed} passed{RESET}, {RED}{failed} failed{RESET}, {total} total")
    if passed == total:
        print(f"{GREEN}{BOLD}All queries returned valid responses!{RESET}")
    print(f"{BOLD}{'=' * 60}{RESET}\n")


if __name__ == "__main__":
    print(f"\n{BOLD}{GREEN}Loading Baker with 208-entry knowledge base...{RESET}")
    import time
    start = time.time()

    init_test = bot.respond("Hello")
    elapsed = time.time() - start

    print(f"  Load time: {elapsed:.3f}s")
    print(f"  Initial response: {CYAN}{init_test}{RESET}")
    print(f"  Intents loaded: {len(bot.list_intents())}")
    print()

    import sys
    if "--test" in sys.argv:
        run_test_suite()
    elif "--interactive" in sys.argv or "-i" in sys.argv:
        interactive_mode()
    else:
        run_test_suite()
        print("Pass --interactive or -i for interactive mode.")
        print()

        print("Quick demo (7 sample exchanges with memory):")
        bot_with_mem = Chatbot("Baker", "knowledge_base.json", backend='tfidf', memory=True,
                               threshold=0.25, intent_threshold=0.2)
        for intent in bot.list_intents():
            bot_with_mem.add_intent(intent, *bot.parser.intent_classifier.intents[intent].values())
        samples = [
            "Hello",
            "My name is Alex",
            "How are you",
            "tell me about black holes",
            "tell me about python programming",
            "who invented the telephone",
            "Goodbye",
        ]
        for q in samples:
            d = bot_with_mem.respond_detailed(q)
            print(f"  {DIM}{q:<35}{RESET} → {CYAN}{d['response'][:60]}{RESET}")
            ctx = bot_with_mem.get_context()
            if ctx and ctx.get('entities'):
                print(f"  {'':35}  {DIM}entities: {ctx['entities']}{RESET}")
