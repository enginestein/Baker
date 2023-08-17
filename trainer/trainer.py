import os
import json
import yaml
import xml.etree.ElementTree as ET
import random

import os
import json
import yaml
import xml.etree.ElementTree as ET
import random

class Trainer:
    def __init__(self, response_file_name):
        self.file_path = response_file_name
        self.responses = self.load_responses(self.file_path)
        
    def load_responses(self, file_path):
        _, file_extension = os.path.splitext(file_path)
        with open(file_path, 'r') as file:
            if file_extension == '.json':
                responses = json.load(file)
            elif file_extension == '.yaml' or file_extension == '.yml':
                responses = yaml.safe_load(file)
            elif file_extension == '.xml':
                root = ET.parse(file).getroot()
                responses = {}
                for item in root:
                    key = item.tag
                    value = [child.text for child in item]
                    responses[key] = value
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
        return responses
    
    def save_responses(self):
        _, file_extension = os.path.splitext(self.file_path)
        with open(self.file_path, 'w') as file:
            if file_extension == '.json':
                json.dump(self.responses, file, indent=4)
            elif file_extension == '.yaml' or file_extension == '.yml':
                yaml.dump(self.responses, file, default_flow_style=False)
            elif file_extension == '.xml':
                root = ET.Element('responses')
                for key, values in self.responses.items():
                    item = ET.SubElement(root, key)
                    for value in values:
                        ET.SubElement(item, 'response').text = value
                tree = ET.ElementTree(root)
                tree.write(file, encoding="utf-8", xml_declaration=True)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
    def train_response(self, user_input, new_response):
        if user_input in self.responses:
            self.responses[user_input].append(new_response)
        else:
            self.responses[user_input] = [new_response]
        self.save_responses()
        
    def get_response(self, user_input):
        if user_input in self.responses:
            return random.choice(self.responses[user_input])
        else:
            return "I'm not sure how to respond to that."