# Neurosymbolic Library System

A neurosymbolic system that answers natural-language questions about a
university library-lending domain. A large language model (LLM) extracts
the facts and the query from a sentence, and Prolog performs the reasoning,
so the answers are logical derivations and cannot be hallucinated.

## How it works

The system follows a decoupled pipeline:

1. **LLM extraction** — the sentence is converted into a JSON object
   containing the facts and the query (using qwen2.5 through Ollama).
2. **Entity resolution** — Python maps the names and titles to the
   identifiers used in the knowledge base.
3. **Prolog reasoning** — the facts are combined with the rules in
   `library.pl`, and SWI-Prolog computes the answer.
4. **Answer** — the result is returned as a yes/no answer, an explanation,
   or a list of suggested books.

## Requirements

- Python 3.10
- SWI-Prolog 10.0.2
- Ollama 0.32.6 with the `qwen2.5` model
- The Python dependency `requests` (see `requirements.txt`)

## Installation and usage

1. Clone the repository:
   
git clone https://github.com/M7yassin/Neurosymbolic-library-system.git

2. Install the Python dependency:
   
pip install -r requirements.txt

3. Pull the model and start the Ollama server (keep it running):

ollama pull qwen2.5

ollama serve

4. Run the system:

python demo.py

## Example

Input: Sara borrowed the pragmatic programmer on day 169. Is it overdue?

The system extracts the fact `borrowed(u05, i04, 169)`, runs the goal
`is_overdue(u05, i04)`, and returns:

Yes.
