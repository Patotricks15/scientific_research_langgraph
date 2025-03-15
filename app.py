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
    retriever = ArxivRetriever(load_max_docs=8, get_ful_documents=True)
    docs = retriever.invoke(state['question'][0])
    result = {"context": [i.page_content for i in docs]}
    return result

    
def generate_summary(state):
    """
    Generates an answer of the given question using the context provided.

    Args:
        state (dict): A dictionary containing the following keys:
            - 'context' (str or list): The context to use when generating the summary.
            - 'question' (list): A list of strings where the first element is the question to be answered.

    Returns:
        dict: A dictionary containing the key 'pre_answers' with the generated summary as its value.
    """
    llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)
    context = state['context']
    question = state['question'][0]
    answer_text = []
    for i in context:
        answer_template = "Answer the question {question} in a summarized form using this context: {context}"
        answer_instructions = answer_template.format(question=question, context=i)
        answer = llm.invoke(answer_instructions)
        answer_text.append(answer.content if hasattr(answer, "content") else str(answer))
    result = {"pre_answers": answer_text}
    return result

def final_answer(state):
    """
    Generates a final and unified answer to a given question using pre-existing answers.

    Args:
        state (dict): A dictionary containing the following keys:
            - 'pre_answers' (str): Pre-existing answers that will be used to form the final answer.
            - 'question' (list): A list where the first element is the question that needs to be answered.

    Returns:
        dict: A dictionary containing the key 'final_output' with the generated final answer as its value.
    """

    llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)
    pre_answers = state['pre_answers']
    question = state['question'][0]
    answer_template = "Write a final and unified answer to the question {question} following this pre-answers {pre_answers}"
    answer_instructions = answer_template.format(pre_answers=pre_answers, question=question)
    final_answer_result = llm.invoke(answer_instructions)
    final_answer_text = final_answer_result.content if hasattr(final_answer_result, "content") else str(final_answer_result)
    result = {"final_output": final_answer_text}
    return result

class State(TypedDict):
    question: Annotated[list, operator.add]
    pre_answers: Annotated[list, operator.add]
    context: Annotated[list, operator.add]
    final_output: str

builder_arxiv = StateGraph(State)
builder_arxiv.add_node("search_arxiv",search_arxiv)
builder_arxiv.add_node("generate_summary",generate_summary)
builder_arxiv.add_node("final_answer",final_answer)

builder_arxiv.add_edge(START, "search_arxiv")
builder_arxiv.add_edge("search_arxiv", "generate_summary")
builder_arxiv.add_edge("generate_summary", "final_answer")
builder_arxiv.add_edge("final_answer", END)

graph = builder_arxiv.compile()
    

while True:
    question = input("Enter your question: ")

    initial_state = {"question": [question]}

    final_state = graph.invoke(initial_state)    

    print(graph.invoke({"question":[question]}))