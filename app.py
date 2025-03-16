from typing_extensions import TypedDict
import operator
from typing import Annotated
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.retrievers import ArxivRetriever
from pylatex import Document, Section, Command
from pylatex.utils import NoEscape
from datetime import datetime
load_dotenv()

llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)

def format_doc(i):
    """
    Formats an Arxiv document into a string format.

    Args:
        i (Document): Arxiv document

    Returns:
        str: Formatted string containing the document's content, published year, title, and authors.
    """
    return (
        "content: " + i.page_content + "\n"
        + "published_year: " + f"{i.metadata['Published']}" + "\n"
        + "Title: " + i.metadata['Title'] + "\n"
        + "Authors: " + i.metadata['Authors']
    )
def search_arxiv(state):
    """
    Performs a search on arXiv and retrieves search results.

    Args:
        state (dict): A dictionary containing the key 'question' with a list 
                      where the first element is the search query.

    Returns:
        dict: A dictionary containing the key 'context' with the retrieved documents.
    """
    retriever = ArxivRetriever(load_max_docs=4, get_ful_documents=True)
    docs = retriever.invoke(state['question'][0])
    result = {"context": [format_doc(i) for i in docs]}
    return result

    
def generate_citation(state):
    """
    Generates an answer of the given question using the context provided.

    Args:
        state (dict): A dictionary containing the following keys:
            - 'context' (str or list): The context to use when generating the summary.
            - 'question' (list): A list of strings where the first element is the question to be answered.

    Returns:
        dict: A dictionary containing the key 'pre_answers' with the generated summary as its value.
    """
    context = state['context']
    question = state['question'][0]
    answer_text = []
    for i in context:
        answer_template = "Answer the question {question} in a scientific form with correct citations using this context: {context}"
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

    pre_answers = state['pre_answers']
    question = state['question'][0]
    answer_template = "Write a final and unified scientific paragraph to answer the question {question} following these pre-answers {pre_answers}. PLEASE mantain the scientific form and correct citations. At the final generate the bibliography in ABNT format."
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
builder_arxiv.add_node("generate_citation",generate_citation)
builder_arxiv.add_node("final_answer",final_answer)

builder_arxiv.add_edge(START, "search_arxiv")
builder_arxiv.add_edge("search_arxiv", "generate_citation")
builder_arxiv.add_edge("generate_citation", "final_answer")
builder_arxiv.add_edge("final_answer", END)

graph = builder_arxiv.compile()
    
def generate_latex(input, final_output):
    """
    Generates a LaTeX document from the provided string and saves it to a .tex file.

    Args:
        final_output (str): The final unified answer text.

    Returns:
        None
    """
    doc = Document()

    doc_title = input
    doc.preamble.append(Command('title', doc_title))
    doc.preamble.append(Command('author', 'Arxiv Agent'))
    doc.preamble.append(Command('date', NoEscape(r'\today')))

    doc.append(NoEscape(r'\maketitle'))

    with doc.create(Section('Final Answer')):
        doc.append(final_output)

    doc.generate_tex("latex_outputs/" + input.replace(" ", "_").lower())

    return None

while True:
    question = input("Enter your question: ")

    initial_state = {"question": [question]}

    final_state = graph.invoke(initial_state)    

    print(graph.invoke({"question":[question]})['final_output'])

    generate_latex(question, graph.invoke({"question":[question]})['final_output'])