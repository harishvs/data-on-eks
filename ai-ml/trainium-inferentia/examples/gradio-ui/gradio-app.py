import json
import gradio as gr
import requests
from load_files import (
    create_chroma_collections,
)


# Constants for model endpoint and service name
model_endpoint = "/predict"
service_name = "http://k8s-ingressn-ingressn-d5a385da81-7cb7eb31b9e9ce36.elb.us-west-2.amazonaws.com/serve"
# service_name = "http://localhost:8000"  # Replace with your actual service name


SYSTEM_PROMPT = """
You are a helpful ecommerce assistant for Anytoy company. 
If you cannot find the answer in the context you will say "I dont know, can i transfer you to a human assistant?"
Don't show any products that are not in context
Don't discuss politics or relegion or drugs or weapons
show emojis
"""


# Formatting function for message and history
def format_message(message: str, history: list, memory_limit: int = 3) -> str:
    """
    Formats the message and history for the Llama model.

    Parameters:
        message (str): Current message to send.
        history (list): Past conversation history.
        memory_limit (int): Limit on how many past interactions to consider.

    Returns:
        str: Formatted message string
    """
    # always keep len(history) <= memory_limit
    if len(history) > memory_limit:
        history = history[-memory_limit:]

    search_results = collection.query(
        query_texts=[message],
        n_results=10,
        include=["documents", "distances", "metadatas"],
    )
    q_context=filter_results(search_results)
    # json_dict = {
    #     "instruction": message,
    #     "context": str(q_context).replace('"', "'"),
    #     "response": "",
    #     "category": "closed_qa",
    # }
    # print(json.dumps(json_dict))
    print(q_context)
    instruction = f"### Instruction\n{message}"
    context = f"### Context\n{q_context}" if q_context else None
    response = f"### Answer\n"
    # join all the parts together
    prompt = "\n\n".join([i for i in [instruction, context, response] if i is not None])

    return SYSTEM_PROMPT + prompt

def filter_results(search_results):
    filtered_results = ""
    for i,distance in enumerate(search_results["distances"][0]):    
        if distance <= 0.6:
            filtered_results+=search_results["documents"][0][i]
    return filtered_results
    
# Function to generate text
def text_generation(message, history):
    prompt = format_message(message, history, 4)
    url = f"{service_name}{model_endpoint}"

    try:
        # Send the request to the model service
        input_json = {"sentence": prompt}
        response = requests.post(url, json=input_json, timeout=180)
        response.raise_for_status()  # Raise an exception for HTTP errors
        generated_text = bytes(response.text, "utf-8").decode("unicode_escape")
        generated_text = generated_text.replace('["', "")
        generated_text = generated_text.replace('"]', "")
        # print(generated_text)
        answer_only = filter_harmful_content(generated_text)
        answer_only = answer_only[1:-1].strip()
        # print(answer_only)
        return answer_only # take out the quotes at beginning and end
    except requests.exceptions.RequestException as e:
        # Handle any request exceptions (e.g., connection errors)
        return f"AI: Error: {str(e)}"



# Define the safety filter function (you can implement this as needed)
def filter_harmful_content(text):
    # TODO: Implement a safety filter to remove any harmful or inappropriate content from the text

    # For now, simply return the text as-is
    return text


# Define the Gradio ChatInterface
chat_interface = gr.ChatInterface(
    text_generation,
    textbox=gr.Textbox(
        placeholder="I am ecommerce assistant for Anytoy company, ask me questions",
        container=False,
        scale=7,
    ),
    title="Any toy company",
    description="Ask me about our products",
    theme="soft",
    examples=["Show me some sling shots?"],
    cache_examples=True,
    retry_btn=None,
    undo_btn="Delete Previous",
    clear_btn="Clear"
)


def main():
    # Launch the ChatInterface
    chat_interface.launch()



collection = create_chroma_collections()
main()
