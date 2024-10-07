import json
import os
from openai import AzureOpenAI

def load_config(config_file):
    with open(config_file, 'r') as file:
        config = json.load(file)
    return config

def test_connection(config):
    try:
        client = AzureOpenAI(
            api_key=config["AZURE_API_KEY"],
            api_version=config["AZURE_API_VERSION"],
            azure_endpoint=config["AZURE_ENDPOINT"]
        )
        models = client.models.list()  #
        print("Connection established successfully! Available models:")
        for model in models.data:
            print(f"- {model.id}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    config_path = 'configs.json'

    if os.path.exists(config_path):
        print("File Found!")
        config = load_config(config_path)
        print(config)

        test_connection(config)
    else:
        print("File not Found!")
