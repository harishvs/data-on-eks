import requests
import re
from load_files import load_text_to_vectordb,load_vector_store
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.chains import ConversationalRetrievalChain
from fast_api_llm import AnyFastAPILlm
import streamlit as st
from streamlit_chat import message
from langchain.memory import ConversationBufferMemory


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
    Please use respectful language and no icons.
    Please don't respond to questions about politics or religion.
    History: 
    {chat_history}
    Context: 
    {context}
    
    Question: 
    {question}
    
    Answer: 
    """

    prompt = PromptTemplate(
        template=template,
        input_variables=['context', 'question', 'chat_history'])
    return prompt

def create_qa_chain(memory):
    """create the qa chain"""

    # load the llm, vector store, and the prompt
    llm = load_llm()
    db = load_vector_store()
    prompt = create_prompt_template()


    # create the qa_chain
    retriever = db.as_retriever(search_kwargs={'k': 2})
    qa_chain = ConversationalRetrievalChain.from_llm(llm=llm,chain_type='stuff',
                                              retriever=retriever,
                                              combine_docs_chain_kwargs={"prompt": prompt},
                                              memory=memory)
    
    return qa_chain

def conversation_chat(query,chain):
    print(st.session_state['history'])
    result = chain({"question": query, "chat_history": st.session_state['history']})
    st.session_state['history'].append((query, result["answer"]))
    return result["answer"]

def initialize_session_state():
    if 'history' not in st.session_state:
        st.session_state['history'] = []

    if 'generated' not in st.session_state:
        st.session_state['generated'] = ["Hello! Ask me anything about Toys"]

    if 'past' not in st.session_state:
        st.session_state['past'] = ["Hey! 👋"]

def display_chat_history(chain):
    reply_container = st.container()
    container = st.container()

    with container:
        with st.form(key='my_form', clear_on_submit=True):
            user_input = st.text_input("Question:", placeholder="Ask me about toys", key='input')
            submit_button = st.form_submit_button(label='Send')

        if submit_button and user_input:
            output = conversation_chat(user_input,chain)

            st.session_state['past'].append(user_input)
            st.session_state['generated'].append(output)

    if st.session_state['generated']:
        with reply_container:
            for i in range(len(st.session_state['generated'])):
                message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="thumbs")
                message(st.session_state["generated"][i], key=str(i), avatar_style="fun-emoji")


def main():
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    st.set_page_config(page_title='Anytoy customer service',layout="wide")
    st.header('Anytoy customer service :robot_face:')
        # initialize message history
    debug = True
    load_text_to_vectordb()
    qa_chain = create_qa_chain(memory)
    # Initialize session state
    initialize_session_state()
    # Display chat history
    display_chat_history(qa_chain)
            
if __name__ == '__main__':
    main()
