from typing_extensions import TypedDict
import operator
from typing import Annotated
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.retrievers import ArxivRetriever

load_dotenv()

def search_arxiv(state):
    """
    Performs a search on arXiv and retrieves search results.

    Args:
        state (dict): A dictionary containing the key 'question' with a list 
                      where the first element is the search query.

    Returns:
        dict: A dictionary containing the key 'context' with the retrieved documents.
    """
    try:
        retriever = ArxivRetriever(load_max_docs=8, get_ful_documents=True)
        docs = retriever.invoke(state['question'][0])
        result = {"context": [docs.page_content]}
        return result
    except:
        return {"context": []}
    
