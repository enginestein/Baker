# Baker

*Bot-Maker* Baker — a chatbot framework with actual ML. Uses TF-IDF vectorization, character n-gram similarity, intent classification, smart response selection, template rendering, and optional sentence-transformers for semantic matching. No hardcoded rules, no massive synonym dictionaries — the ML learns from your data.

# Installation

```bash
pip install baker-python
```

Or from source:

```bash
pip install -e .
```

For the semantic backend (better understanding, heavier dependency):

```bash
pip install sentence-transformers
```

# Quick Start

```python
from baker import Chatbot

bot = Chatbot("MyBot", "data.json", memory=True)

# Define intents (optional — checked before fuzzy matching)
bot.add_intent("greeting", ["Hello", "Hi", "Howdy"], ["Hey there!", "Hi {name}!"])

bot.respond("Hello")            # "Hey there!" (via intent)
bot.respond("helloo")           # understands typos via char n-gram TF-IDF
bot.respond("how are you doing?")   # matches via word TF-IDF
bot.respond("whats your name")      # "whats" → "what is" via contraction expansion
bot.respond("My name is Alice")     # "Hi Alice!" (template + entity extraction)
```

## How the ML Works

Baker uses a **two-vector approach** for matching:

1. **Word-level TF-IDF**: Learns term importance from your data. Common words get lower weight, distinctive words get higher weight. Queries are compared to known keys via cosine similarity.

2. **Character n-gram TF-IDF** (2-4 grams): Captures spelling variations, typos, and morphological similarity. "helloo" → shares character n-grams with "Hello".

Combined score: `0.6 × word_sim + 0.4 × char_sim`

## Data File Format

Create a JSON, YAML, or XML file:

**JSON** (`data.json`):
```json
{
    "Hello": ["Hi!", "Hello!", "Hey there!"],
    "How are you": ["I'm doing great!", "Pretty good, thanks!"],
    "What is your name": ["My name is Baker!"]
}
```

**YAML** (`data.yaml`):
```yaml
Hello:
- Hi!
- Hello!
How are you:
- I'm good, thanks!
```

**XML** (`data.xml`):
```xml
<responses>
  <Hello>
    <response>Hi!</response>
    <response>Hello!</response>
  </Hello>
</responses>
```

# Usage

## Constructor Parameters

Additional `Chatbot` constructor options:

```python
# Custom sentence-transformers model for semantic backend
bot = Chatbot("MyBot", "data.json", backend='semantic', model_name='all-mpnet-base-v2')

# Custom intent classification threshold (default 0.3)
bot = Chatbot("MyBot", "data.json", intent_threshold=0.5)

# Adjust word vs character n-gram weighting in combined score (default 0.6/0.4)
bot = Chatbot("MyBot", "data.json", threshold=0.3)
```

To adjust the Matcher's word/char weight ratio directly:

```python
from baker import Matcher
matcher = Matcher(threshold=0.3, word_weight=0.7, char_weight=0.3)
```

## Backend Selection

| Backend | Dependency | Quality | Use Case |
|---------|-----------|---------|----------|
| `'tfidf'` (default) | none | Good | Lightweight, fast, no installs |
| `'semantic'` | sentence-transformers | Best | Deep semantic understanding |

```python
# Default TF-IDF (lightweight ML, no extra deps)
bot = Chatbot("MyBot", "data.json", backend='tfidf')

# Semantic (requires: pip install sentence-transformers)
bot = Chatbot("MyBot", "data.json", backend='semantic')
```

## Intents

Define named intents with example phrases and responses. Baker classifies user input via TF-IDF against your examples.

```python
bot.add_intent(
    "greeting",
    ["Hello", "Hi", "Hey", "Howdy", "Good morning"],
    ["Hey there!", "Hi {name}!", "Hello! How are you?"]
)

bot.add_intent(
    "farewell",
    ["Bye", "Goodbye", "See you later"],
    ["Goodbye!", "See you later!", "Take care {name}!"]
)

bot.list_intents()  # ["greeting", "farewell"]
bot.remove_intent("farewell")
```

Intents are checked **before** fuzzy TF-IDF key matching, so they override ambiguous matches.

Negative examples refine intent discrimination — phrases that should **not** match:

```python
bot.add_intent(
    "greeting",
    ["Hello", "Hi", "Hey"],
    ["Hey there!"],
    negative_examples=["Hell is hot", "High five"]
)
```

## Template Responses

Responses can use `{variable}` placeholders filled from entities and conversation memory:

```python
bot.respond("My name is Alice")  # "Hi Alice!" (from greeting intent + entity)
```

Available variables: `{name}`, `{age}`, `{email}`, `{last_topic}`, `{sentiment}`, `{intent}`. Unknown variables keep their raw `{variable}` placeholder.

Entities extracted from user input: `name`, `age`, `email`, and `numbers`.

## Smart Response Selection

Instead of random choice, Baker scores each response candidate:

- **+1.0** base score
- **−0.3** per recent use (last 5 responses)
- **+0.15** per matched entity in the text
- **+0.05** for templates (encourages personalized responses)

This naturally avoids repetition and prefers responses that reference extracted entities.

## Training

```python
# Single
bot.train("Hello", "Hey there!")

# Bulk
bot.train_many([
    ("What is your name", "I'm Baker!"),
    ("How old are you", "I was just born!"),
])

# From a JSON corpus file
trainer = Trainer("data.json")
trainer.train_from_json("corpus.json")
trainer.train_from_csv("corpus.csv")                # default: question_col=0, response_col=1, has_header=True
trainer.train_from_txt("corpus.txt", separator='|') # each line: question | response
trainer.train_from_yaml("corpus.yaml")
trainer.auto_learn([("Hi", "Hello"), ("Bye", "Goodbye")])
trainer.loop_training()        # interactive question/response loop
trainer.interactive_session()  # pipe-format training session (type "exit" to quit)
```

Parser can also save in-memory changes back to file:

```python
parser = Parser("data.json")
parser.load_responses("other.json")  # load from a different file
parser.add_intent("greeting", ["Hi"], ["Hello!"])
parser.train_response("Hi", "Hey there!")  # adds + saves
parser.save_responses()                    # persist to original file
```

## Response Details

```python
details = bot.respond_detailed("Hello")
print(details['response'])     # "Hi!"
print(details['confidence'])   # 1.0
print(details['matched_key'])  # "Hello"
print(details['sentiment'])    # "neutral"
print(details['entities'])     # {}
print(details['backend'])      # "tfidf"
print(details['intents'])      # ["greeting", "farewell"]
```

## Conversation Memory

```python
bot = Chatbot("MyBot", "data.json", memory=True)
bot.respond("My name is Alice")
bot.get_context()['entities']['name']  # "Alice"
bot.get_context()['history']           # recent exchanges
bot.get_context()['last_topic']        # most mentioned topic
bot.get_context()['exchange_count']    # total turns so far
```

```python
from baker import ConversationMemory

mem = ConversationMemory(max_history=20)
mem.add("Hello", "Hi there!", entities={"name": "Alice"})
mem.get_last_user_input()   # "Hello"
mem.get_last_bot_response() # "Hi there!"
mem.has_entity("name")      # True
mem.get_entity("name")      # "Alice"
mem.detect_reference("it is great")  # True (reference word detected)
mem.get_conversation_summary()  # "User: Alice | Topics: ... | 1 exchanges"
mem.clear()
```

## Adjusting Match Sensitivity

```python
# Lower threshold = more fuzzy matches (default 0.3)
bot = Chatbot("MyBot", "data.json", threshold=0.2)

# Higher threshold = stricter matching
bot = Chatbot("MyBot", "data.json", threshold=0.6)
```

## Data Management

```python
from baker import Parser

parser = Parser("data.json")
parser.list_key_questions()
parser.count_responses("Hello")
parser.remove_response("Hello", "Hi")
parser.reset_responses("Hello")
parser.export_responses("data.yaml")

# With context for template rendering
context = bot.get_context()
parser.get_response("Hello", context=context)

# With confidence score
response, confidence = parser.get_response("Hello", return_confidence=True)
```

## Last Response

```python
bot.respond("Hello")      # "Hi!"
bot.get_last_response()   # "Hi!"
```

## Interactive Session

```python
bot = Chatbot("MyBot", "data.json")
bot.session()
```

Type `teach` to train the bot mid-session.

# API

| Class | Purpose |
|-------|---------|
| `Chatbot(name, data_file, backend, threshold, memory, model_name, intent_threshold)` | Main chatbot interface |
| `Parser(file, backend, threshold, model_name, intent_threshold)` | Data layer with ML matching. Attributes: `responses`, `matcher`, `entity_extractor`, `sentiment_analyzer`, `intent_classifier`, `response_selector`, `template_engine`, `processor` |
| `Trainer(file, backend, threshold)` | Extends Parser with bulk training |
| `Matcher(threshold)` | TF-IDF + char n-gram similarity search |
| `SemanticMatcher(model, threshold)` | Sentence-transformers similarity |
| `TfidfVectorizer(use_stopwords=True)` | Pure-Python TF-IDF implementation |
| `CharNgramVectorizer(n_min=2, n_max=4)` | Character n-gram TF-IDF vectorization |
| `TextProcessor()` | Text normalization (contraction expansion, tokenization, stopword removal) |
| `IntentClassifier(threshold)` | TF-IDF intent classification from examples |
| `ResponseSelector(recency_penalty, diversity_window)` | Smart non-random response selection. `select(responses, entities)` scores candidates; `reset()` clears history |
| `TemplateEngine()` | `{variable}` placeholder rendering in responses |
| `EntityExtractor()` | Regex entity extraction (name, age, email) |
| `SentimentAnalyzer()` | Token-based sentiment detection |
| `ConversationMemory()` | Conversation history and entity tracking |

A pre-built knowledge base (`knowledge_base.json`) with 200+ entries across science, technology, history, health, nature, and philosophy is included:

```python
bot = Chatbot("Demo", "knowledge_base.json")
bot.session()
```

# Why Baker?

- **Real ML**: TF-IDF vectorization + cosine similarity. No hardcoded rules.
- **Lightweight default**: Zero external ML dependencies (only PyYAML for file formats).
- **Optional semantic power**: Plug in sentence-transformers for deep understanding.
- **Simple**: One-liner instantiation, one method to chat.
- **Flexible**: JSON, YAML, XML. Train on the fly or from files.

# License

GNU General Public License v3.0
