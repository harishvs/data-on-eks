"""
This script creates a database of information gathered from local text files.
"""
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


def load_text_to_vectordb():
    # define what documents to load
    loader = DirectoryLoader("data", glob="*.txt", loader_cls=TextLoader)
    # interpret information in the documents
    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500,
                                              chunk_overlap=50)
    texts = splitter.split_documents(documents)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'})
    # create and save the local database
    db = FAISS.from_documents(texts, embeddings)
    db.save_local("faiss")


def load_vector_store():
    # load the vector store
    
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'})
    db = FAISS.load_local("faiss", embeddings)
    return db

if __name__ == '__main__':
    load_text_to_vectordb()
