"""
This script creates a database of information gathered from local text files.
"""

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from chroma_utils import build_chroma_collection
import chromadb
from chromadb.utils import embedding_functions

DATA_PATH = "data/archive/*"
CHROMA_PATH = "product_data_embeddings"
EMBEDDING_FUNC_NAME = "multi-qa-MiniLM-L6-cos-v1"
COLLECTION_NAME = "product_data5"


def load_text_to_vectordb():
    # define what documents to load
    loader = DirectoryLoader("data", glob="*.txt", loader_cls=TextLoader)
    # interpret information in the documents
    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = splitter.split_documents(documents)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
    )
    # create and save the local database
    db = FAISS.from_documents(texts, embeddings)
    db.save_local("faiss")


def load_vector_store():
    # load the vector store
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
    )
    db = FAISS.load_local("faiss", embeddings)
    return db

def split_documents(documents):
    split_texts = []
    for document in documents:
        split_texts.extend(document.page_content.split('\n'))
    return split_texts

def create_chroma_collections():
    loader = DirectoryLoader("data", glob="*.txt", loader_cls=TextLoader)
    # interpret information in the documents
    documents = loader.load()
    texts = split_documents(documents)
    # for i,text in enumerate(texts):
    #     print(i,'.', text)
    ids = [str(i) for i in range(len(texts))]
    metadatas = [None for i in range(len(texts))]
    chroma_product_data_dict = {"ids": ids, "documents": texts, "metadatas": metadatas}

    return build_chroma_collection(
        CHROMA_PATH,
        COLLECTION_NAME,
        EMBEDDING_FUNC_NAME,
        chroma_product_data_dict["ids"],
        chroma_product_data_dict["documents"],
        chroma_product_data_dict["metadatas"],
    )

    
    

if __name__ == "__main__":
    load_text_to_vectordb()
