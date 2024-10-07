import json
import os
import time
from openai import AzureOpenAI

class OrchestrationManager:
    def __init__(self, config_file):
        self.load_config(config_file)
        self.client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.azure_endpoint
        )
        self.assistant_id = None

    def load_config(self, config_file):
        with open(config_file, 'r') as file:
            config = json.load(file)
            self.api_key = config["AZURE_API_KEY"]
            self.api_version = config["AZURE_API_VERSION"]
            self.azure_endpoint = config["AZURE_ENDPOINT"]

    def find_assistant_by_name(self, assistant_name):
        response = self.client.beta.assistants.list()

        for assistant in response.data:
            if assistant.name == assistant_name:
                self.assistant_id = assistant.id
                print(f"Found assistant: {assistant.name} [ID: {assistant.id}]")
                return

        if self.assistant_id is None:
            print(f"No assistant found with name: {assistant_name}")

    def create_thread_and_send_message(self, question):
        if self.assistant_id is None:
            print("No assistant ID found. Please check the assistant name.")
            return

        thread = self.client.beta.threads.create()
        print(f"Thread created with ID: {thread.id}")

        message = self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question
        )
        print(f"Message sent with ID: {message.id}")

        return thread

    def run_thread(self, thread, instructions):
        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self.assistant_id,
            instructions=instructions
        )
        print(f"Run started with ID: {run.id}")

        return run

    def wait_for_completion(self, thread, run):
        while True:
            time.sleep(5)

            run_status = self.client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run_status.status == 'completed':
                print("Run completed. Retrieving messages...")
                self.display_conversation(thread)
                break
            elif run_status.status == 'requires_action':
                print("Assistant requires further action.")
                self.handle_required_action(run_status, thread, run)
            else:
                print("Waiting for the Assistant to process...")

    def display_conversation(self, thread):
        messages = self.client.beta.threads.messages.list(thread_id=thread.id)

        for msg in messages.data:
            role = msg.role
            content = msg.content[0].text.value
            print(f"{role.capitalize()}: {content}")

    def handle_required_action(self, run_status, thread, run):
        print("Handling function calls from assistant...")
        required_actions = run_status.required_action.submit_tool_outputs.model_dump()

        tool_outputs = []
        for action in required_actions["tool_calls"]:
            func_name = action['function']['name']
            arguments = json.loads(action['function']['arguments'])
            output = globals()[func_name](**arguments)
            tool_outputs.append({
                "tool_call_id": action['id'],
                "output": output
            })

        self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )


if __name__ == "__main__":
    config_path = 'configs.json'

    if os.path.exists(config_path):
        print("File Found!")
        assistant_name = "CSV File Analyst Assistant POC v1.3"
        instructions = "Display only the names of files that I have uploaded to you"
        question = "Count the number of columns in the sample file."

        manager = OrchestrationManager(config_path)

        manager.find_assistant_by_name(assistant_name)

        thread = manager.create_thread_and_send_message(question)

        if thread:
            run = manager.run_thread(thread, instructions)

            manager.wait_for_completion(thread, run)
    else:
        print("File not Found!")
