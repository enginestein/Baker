import json
import random
import os
import yaml
import xml.etree.ElementTree as ET

class Parser:
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
        
    def remove_response(self, user_input, response):
        if user_input in self.responses and response in self.responses[user_input]:
            self.responses[user_input].remove(response)
            self.save_responses()
    
    def list_key_questions(self):
        return list(self.responses.keys())
    
    def count_responses(self, user_input):
        if user_input in self.responses:
            return len(self.responses[user_input])
        else:
            return 0
    
    def reset_responses(self, user_input):
        if user_input in self.responses:
            self.responses[user_input] = []
            self.save_responses()
            
    def export_responses(self, export_file_name):
        export_extension = os.path.splitext(export_file_name)[1]

        with open(export_file_name, 'w') as export_file:
            if export_extension == '.json':
                json.dump(self.responses, export_file, indent=4)
            elif export_extension == '.yaml' or export_extension == '.yml':
                yaml.dump(self.responses, export_file, default_flow_style=False)
            elif export_extension == '.xml':
                root = ET.Element('responses')
                for key, values in self.responses.items():
                    item = ET.SubElement(root, key)
                    for value in values:
                        ET.SubElement(item, 'response').text = value
                tree = ET.ElementTree(root)
                tree.write(export_file, encoding="utf-8", xml_declaration=True)
            else:
                raise ValueError(f"Unsupported export file format: {export_extension}")