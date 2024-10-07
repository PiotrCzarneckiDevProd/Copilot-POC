import json
import os
from openai import AzureOpenAI

class DeletionManager:
    def __init__(self, config_file):
        self.load_config(config_file)
        
        self.client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.azure_endpoint
        )

    def load_config(self, config_file):
        with open(config_file, 'r') as file:
            config = json.load(file)
            self.api_key = config["AZURE_API_KEY"]
            self.api_version = config["AZURE_API_VERSION"]
            self.azure_endpoint = config["AZURE_ENDPOINT"]

    def delete_all_files(self):
        response = self.client.files.list(purpose="assistants API")
        if len(response.data) == 0:
            print("No files found to delete.")
            return

        for file in response.data:
            self.client.files.delete(file.id)
            print(f"Deleted file: {file.filename} [{file.id}]")

        print("All files have been successfully deleted.")

    def delete_specific_assistant(self, assistant_name="File Analyst Assistant POC v1.0"):
        response = self.client.beta.assistants.list()
        if len(response.data) == 0:
            print("No assistants found to delete.")
            return

        for assistant in response.data:
            if assistant.name == assistant_name:
                self.client.beta.assistants.delete(assistant.id)
                print(f"Deleted assistant: {assistant.name} [{assistant.id}]")
                break
        else:
            print(f"No assistant found with the name: {assistant_name}")

if __name__ == "__main__":
    config_path = 'configs.json'

    if os.path.exists(config_path):
        print("File found!")
        file_manager = DeletionManager(config_path)

        file_manager.delete_all_files()
        file_manager.delete_specific_assistant()
    else:
        print("File not found!")
