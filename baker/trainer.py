import os
import json
import csv
import yaml
import xml.etree.ElementTree as ET
import random

from baker.bparser import Parser


class Trainer(Parser):
    def __init__(self, response_file_name, backend='tfidf', threshold=0.3, model_name=None):
        super().__init__(response_file_name, backend=backend, threshold=threshold, model_name=model_name)

    def train_many(self, pairs):
        for question, response in pairs:
            self.train_response(question, response)

    def train_from_json(self, json_file):
        with open(json_file, 'r') as f:
            data = json.load(f)
        if isinstance(data, dict):
            for question, responses in data.items():
                if isinstance(responses, list):
                    for response in responses:
                        self.train_response(question, response)
                else:
                    self.train_response(question, responses)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and 'question' in item and 'response' in item:
                    self.train_response(item['question'], item['response'])

    def train_from_csv(self, csv_file, question_col=0, response_col=1, has_header=True):
        with open(csv_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            if has_header:
                next(reader, None)
            for row in reader:
                if len(row) > max(question_col, response_col):
                    question = row[question_col].strip()
                    response = row[response_col].strip()
                    if question and response:
                        self.train_response(question, response)

    def train_from_txt(self, txt_file, separator='|'):
        with open(txt_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if separator in line:
                    parts = line.split(separator, 1)
                    question = parts[0].strip()
                    response = parts[1].strip()
                    if question and response:
                        self.train_response(question, response)
                else:
                    self.train_response(line, "Interesting, tell me more!")

    def train_from_yaml(self, yaml_file):
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        if isinstance(data, dict):
            for question, responses in data.items():
                if isinstance(responses, list):
                    for response in responses:
                        self.train_response(question, response)
                else:
                    self.train_response(question, responses)

    def auto_learn(self, text_pairs):
        for pair in text_pairs:
            if isinstance(pair, (list, tuple)) and len(pair) >= 2:
                question, response = pair[0], pair[1]
                self.train_response(str(question).strip(), str(response).strip())

    def loop_training(self):
        try:
            while True:
                key_question = input("Enter a key question (or press Ctrl+C to exit): ")
                if key_question:
                    response = input("Enter a response: ")
                    self.train_response(key_question, response)
                    print(f"  Trained: '{key_question}' -> '{response}'")
        except KeyboardInterrupt:
            print("\nTraining aborted.")

    def interactive_session(self):
        print("Interactive Training Session (type 'exit' to stop)")
        print("You can train the bot by typing: question | response")
        try:
            while True:
                line = input("Train: ")
                if line.lower() == 'exit':
                    break
                if '|' in line:
                    parts = line.split('|', 1)
                    question = parts[0].strip()
                    response = parts[1].strip()
                    if question and response:
                        self.train_response(question, response)
                        print(f"  Learned: '{question}'")
                    else:
                        print("  Please use: question | response")
                else:
                    print("  Please use: question | response")
        except KeyboardInterrupt:
            print("\nSession ended.")
