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

## Template Responses

Responses can use `{variable}` placeholders filled from entities and conversation memory:

```python
bot.respond("My name is Alice")  # "Hi Alice!" (from greeting intent + entity)
```

Available variables: `{name}`, `{age}`, `{email}`, `{last_topic}`, `{sentiment}`, `{intent}`. Unknown variables render as empty string.

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
trainer.train_from_csv("corpus.csv")
```

## Response Details

```python
details = bot.respond_detailed("Hello")
print(details['response'])     # "Hi!"
print(details['confidence'])   # 1.0
print(details['matched_key'])  # "Hello"
print(details['sentiment'])    # "neutral"
print(details['entities'])     # {}
```

## Conversation Memory

```python
bot = Chatbot("MyBot", "data.json", memory=True)
bot.respond("My name is Alice")
bot.get_context()['entities']['name']  # "Alice"
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
| `Chatbot(name, data_file, backend, threshold, memory)` | Main chatbot interface |
| `Parser(file, backend, threshold)` | Data layer with ML matching |
| `Trainer(file, backend, threshold)` | Extends Parser with bulk training |
| `Matcher(threshold)` | TF-IDF + char n-gram similarity search |
| `SemanticMatcher(model, threshold)` | Sentence-transformers similarity |
| `TfidfVectorizer()` | Pure-Python TF-IDF implementation |
| `IntentClassifier(threshold)` | TF-IDF intent classification from examples |
| `ResponseSelector(recency_penalty, diversity_window)` | Smart non-random response selection |
| `TemplateEngine()` | `{variable}` placeholder rendering in responses |
| `EntityExtractor()` | Regex entity extraction (name, age, email) |
| `SentimentAnalyzer()` | Token-based sentiment detection |
| `ConversationMemory()` | Conversation history and entity tracking |

# Why Baker?

- **Real ML**: TF-IDF vectorization + cosine similarity. No hardcoded rules.
- **Lightweight default**: Zero external ML dependencies (only PyYAML for file formats).
- **Optional semantic power**: Plug in sentence-transformers for deep understanding.
- **Simple**: One-liner instantiation, one method to chat.
- **Flexible**: JSON, YAML, XML. Train on the fly or from files.

# License

GNU General Public License v3.0
