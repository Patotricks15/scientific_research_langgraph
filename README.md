# Project Documentation: Arxiv Citation Generator

## Objective

This project aims to create an automated system that searches for academic documents on arXiv based on a given question, generates scientific citations using the content of the documents, and compiles these answers into a unified format. The system generates a final answer while maintaining a scientific form, including proper citations in ABNT format, and also generates a LaTeX document with the final answer.

## Features

1. **Arxiv Search**: 
   - Performs a search on arXiv based on the provided question.
   - Retrieves up to 4 relevant documents with the full content.

2. **Citation Generation**: 
   - Uses the content from retrieved documents to answer the provided question in a scientific manner.
   - Answers are based on the context of the documents with correct citations.

3. **Unified Final Answer**:
   - Combines all generated answers into a single unified scientific response.
   - The final answer is generated with citations formatted in ABNT style.

4. **LaTeX Generation**: 
   - Creates a LaTeX document containing the question and final answer.
   - The document is saved as a `.tex` file for later compilation.

## Code Structure

### Functions

1. **`format_doc(i)`**:
   - Formats the content of an Arxiv document into a string with relevant details such as title, publication year, and authors.

2. **`search_arxiv(state)`**:
   - Executes the search on arXiv using the `ArxivRetriever`.
   - Returns a list of formatted documents.

3. **`generate_citation(state)`**:
   - Generates an answer to the question using the content of the retrieved documents.

4. **`final_answer(state)`**:
   - Generates a unified scientific answer with formatted citations.
   - The final answer is based on pre-existing answers.

5. **`generate_latex(input, final_output)`**:
   - Creates a LaTeX document with the title and final answer.
   - Saves the document in the `latex_outputs/` directory.

### Workflow

The workflow is managed by the `StateGraph`, which defines the sequence of nodes:

1. **search_arxiv**: Performs the search on arXiv.
2. **generate_citation**: Generates citations based on the retrieved documents.
3. **final_answer**: Generates the final unified answer with citations.
4. **generate_latex**: Generates the `.tex` file with the final answer.

### Installation

To run the project, you need to install the required dependencies:

```bash
pip install langchain langchain_openai langgraph pylatex dotenv
