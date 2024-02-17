import requests
import re
from load_files import load_text_to_vectordb,load_vector_store
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from fast_api_llm import AnyFastAPILlm
import streamlit as st
from streamlit_chat import message

def get_user_input():
    # get the user query
    input_text = st.text_input('Ask me about our products!', "", key='input')
    return input_text

# Constants for model endpoint and service name
model_endpoint = "/infer"
# service_name = "http://<REPLACE_ME_WITH_ELB_DNS_NAME>/serve"
service_name = "http://localhost:8000"  # Replace with your actual service name

# Create the URL for the inference
url = f"{service_name}{model_endpoint}"

def load_llm():
    """load the llm"""

    llm = AnyFastAPILlm(end_point=url)
    return llm

def create_prompt_template():
    # prepare the template that provides instructions to the chatbot
    template = """
    You are a helpful ecommerce assistant for Any toy company. 
    You help customers with routine queries and help find products. 
    Use the provided context to answer the user's question. 
    If you don't know the answer based on the context, respond with "I do not know, can i transfer you to a human assistant?".
    Please use respectful language and no icons.
    Please don't respond to questions about politics or religion.

    Context: 
    {context}
    
    Question: 
    {question}
    
    Answer: 
    """

    prompt = PromptTemplate(
        template=template,
        input_variables=['context', 'question'])
    return prompt

def create_qa_chain():
    """create the qa chain"""

    # load the llm, vector store, and the prompt
    llm = load_llm()
    db = load_vector_store()
    prompt = create_prompt_template()


    # create the qa_chain
    retriever = db.as_retriever(search_kwargs={'k': 2})
    qa_chain = RetrievalQA.from_chain_type(llm=llm,
                                        chain_type='stuff',
                                        retriever=retriever,
                                        return_source_documents=False,
                                        chain_type_kwargs={'prompt': prompt})
    
    return qa_chain

def generate_response(query, qa_chain):

    # use the qa_chain to answer the given query
    return qa_chain({'query':query})['result']


# Define the safety filter function (you can implement this as needed)
def filter_harmful_content(text):
    # TODO: Implement a safety filter to remove any harmful or inappropriate content from the text

    # For now, simply return the text as-is
    return text

def main():
    st.set_page_config(page_title='Llama2-Chatbot',layout="wide")
    st.header('Anytoy customer service :robot_face:')
        # initialize message history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            SystemMessage(content="You are a helpful assistant.")
        ]
    debug = True
    load_text_to_vectordb()
    qa_chain = create_qa_chain()
    # create empty lists for user queries and responses
    if 'generated' not in st.session_state:
        st.session_state['generated'] = []
    if 'past' not in st.session_state:
        st.session_state['past'] = []

    # get the user query
    user_input = get_user_input()

    if user_input:
        # generate response to the user input
        response = generate_response(query=user_input, qa_chain=qa_chain)
        response = bytes(response, "utf-8").decode("unicode_escape")
        generated_text = response.replace('["', "")
        generated_text = generated_text.replace('"]', "")
        print("generated_text", generated_text)   
        # add the input and response to session state
        
        if not debug:
            print("heeeeee")
            lines = generated_text.splitlines()
            # print(lines)
            answer_index = None
            for i,line in enumerate(lines):
                # print(i,".",line.strip())
                if re.search(r"Answer:",line.strip()):
                    answer_index = i
                    break
            if answer_index is not None:
                if answer_index+1 < len(lines)-1:                
                    generated_text = "\n".join(lines[answer_index+1:])
                else:
                    generated_text = "Shall i transfer to a human"
        st.session_state.past.append(user_input)
        st.session_state.generated.append(generated_text)

    # display conversaion history (if there is one)
    if st.session_state['generated']:
        for i in range(len(st.session_state['generated']) -1, -1, -1):
            message(st.session_state['generated'][i], key=str(i))
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
            
if __name__ == '__main__':
    main()
