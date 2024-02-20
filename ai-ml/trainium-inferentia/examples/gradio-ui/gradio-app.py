import gradio as gr
import requests
from load_files import load_text_to_vectordb,load_vector_store


# Constants for model endpoint and service name
model_endpoint = "/predict"
# service_name = "http://<REPLACE_ME_WITH_ELB_DNS_NAME>/serve"
service_name = "http://localhost:8000"  # Replace with your actual service name


SYSTEM_PROMPT = """<s>[INST] <<SYS>>
You are a helpful ecommerce assistant for Anytoy company. 
You help customers with routine queries about anytoy company and help them find products.
For routine queries about Anytoy company use  metadata source: data/ecomm_faq_chabot_dataset.txt in context
For product queries about Anytoy company use  metadata source: data/product_data.txt in context
If you cannot find the answer in the context you will say "I dont know, can i transfer you to a human assistant?"
Don't Use emoticons.
Don't discuss politics or relegion.
context:
{q_context}
<</SYS>>
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
        
    db = load_vector_store()
    retriever = db.as_retriever(search_kwargs={'k': 5})
    q_context = retriever.get_relevant_documents(message)
    # print(q_context)
  
    if len(history) == 0:
        return SYSTEM_PROMPT.format(q_context=q_context) + f"{message} [/INST]"

    formatted_message = SYSTEM_PROMPT.format(q_context=q_context) + f"{history[0][0]} [/INST] {history[0][1]} </s>"

    # Handle conversation history
    for user_msg, model_answer in history[1:]:
        formatted_message += f"<s>[INST] {user_msg} [/INST] {model_answer} </s>"

    # Handle the current message
    formatted_message += f"<s>[INST] {message}  [/INST]"

    return formatted_message

# Function to generate text
def text_generation(message, history):
    prompt = format_message(message, history,4)
    print(prompt)
    # Create the URL for the inference
    url = f"{service_name}{model_endpoint}"

    try:
        # Send the request to the model service
        # response = requests.get(url, params={"sentence": prompt}, timeout=180)
        input_json = {'sentence': prompt}
        response = requests.post(url, json=input_json, timeout=180)
        response.raise_for_status()  # Raise an exception for HTTP errors
        generated_text = bytes(response.text,"utf-8").decode('unicode_escape')
        generated_text = generated_text.replace('["', "")
        generated_text = generated_text.replace('"]', "")  
        # print(generated_text)
        answer_only = filter_harmful_content(generated_text)
        return format_output(answer_only.strip())
    except requests.exceptions.RequestException as e:
        # Handle any request exceptions (e.g., connection errors)
        return f"AI: Error: {str(e)}"

def format_output(output):
    str_to_find = "[/INST]"
    last_inst_index = output.rfind(str_to_find)
    print("last_inst_index", last_inst_index)
    if last_inst_index == -1:
        return output
    else:
        return output[last_inst_index+len(str_to_find):]

# Define the safety filter function (you can implement this as needed)
def filter_harmful_content(text):
    # TODO: Implement a safety filter to remove any harmful or inappropriate content from the text

    # For now, simply return the text as-is
    return text


# Define the Gradio ChatInterface
chat_interface = gr.ChatInterface(
    text_generation,
    textbox=gr.Textbox(placeholder="Ask me a question", container=False, scale=7),
    title="Any toy company",
    description="Ask me any question",
    theme="soft",
    examples=["Show me some sling shots?"],
    cache_examples=True,
    retry_btn=None,
    undo_btn="Delete Previous",
    clear_btn="Clear",
)

def main():
    # Launch the ChatInterface
    chat_interface.launch()

if __name__ == '__main__':
    load_text_to_vectordb()
    print('---------------loaded text-------------')
    main()