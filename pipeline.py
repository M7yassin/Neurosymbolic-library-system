
import shutil
import subprocess
import tempfile
import os
import json
import requests
import time
from subprocess import run as run

swipl_path = shutil.which("swipl") or r"C:\Program Files\swipl\bin\swipl.exe"

USERS = [
    ("u01", "anna",  "student"),
    ("u02", "bob",   "student"),
    ("u03", "clara", "staff"),
    ("u04", "adam",  "professor"),
    ("u05", "sara",  "professor"),
]

BOOKS = {"introduction to algorithms":"i01",
         "art of prolog":"i02",
         "deep learning":"i03",
         "pragmatic programmer":"i04",
         "artificial intelligence: a modern approach":"i05",
         "sapiens: a brief history of humankind":"i06",
         "silk roads: a new history of the world":"i07",
         "thinking, fast and slow":"i08",
         "power of habit":"i09",
         "educated: a memoir":"i10",
         "name of the rose":"i11",
         "klara and the sun":"i12",
         "kafka on the shore":"i13",
         "da vinci code":"i14",
         "divine comedy":"i15",
         "a brief history of time":"i16",
         "elegant universe":"i17",
         "feynman lectures on physics":"i18",
         "selfish gene":"i19",
         "origin of species":"i20",
         "oxford english dictionary":"i21",
         "merriam-webster dictionary":"i22",
         "math: the language of the universe":"i23",
         "space: the final frontier":"i24",
         "universe in a nutshell":"i25"
}
REASONS={
    "allowed": "This borrowing is allowed.",
    "reference_book": "Not allowed: reference books cannot be borrowed.",
    "rare_book": "Not allowed: this is a rare book (published before 1915) and is restricted.",
    "over_limit":"Not allowed: the user has reached their borrowing limit.",
    "has_overdue":"Not allowed: the user has an overdue book and must return it first.",
    "already_borrowed":"Not allowed: the book is already borrowed by someone else.",
    "reserved_by_other":"Not allowed: the book is reserved by another user, but you can add yourself to the reservation queue."
}


#---JSON To Prolog Facts---

def fact_to_prolog(fact):
    functor = fact["functor"]           
    args = ", ".join(fact["arguments"])  
    return f"{functor}({args})." 

def facts_to_prolog(facts):
    return [fact_to_prolog(fact) for fact in facts]


def resolve_user(name, role=None):
    name=name.strip().lower()
    if name.startswith("u") and name[1:].isdigit():
        return name
    matches = [uid for (uid, n, r) in USERS
               if n == name and (role is None or r == role)]
    if len(matches) == 0:
        raise ValueError(f"Unknown user: {name} (role={role})")
    if len(matches) > 1:
        raise ValueError(f"Ambiguous user: {name} — need role to disambiguate")
    return matches[0]

def resolve_book(title):
    title=title.strip().lower()
    if title.startswith("i") and title[1:].isdigit():
        return title                       
    key = title.strip().lower()
    if key.startswith("the "):
        key = key[4:]
    if key in BOOKS:
        return BOOKS[key]
    raise ValueError(f"Unknown book: {title}")


def resolve(fact):
    f = fact["functor"]
    a = fact["arguments"]
    if f == "user":                      
        uid = resolve_user(a[0], a[1] if len(a) > 1 else None)
        return {"functor": "user", "arguments": [uid, a[0], a[1]]}
    if f in ("borrowed", "reserved"):    
        uid = resolve_user(a[0])
        bid = resolve_book(a[1])
        return {"functor": f, "arguments": [uid, bid] + a[2:]}
    if f in ("is_overdue", "may_borrow"):  
        return {"functor": f, "arguments": [resolve_user(a[0]), resolve_book(a[1])]}
    if f in ("is_available", "is_rare"):   
        return {"functor": f, "arguments": [resolve_book(a[0])]}
    if f=="suggest_all":                  
        return {"functor": f, "arguments": [resolve_user(a[0]), a[1]]}
    if f=="has_any_overdue":
        return {"functor": f, "arguments": [resolve_user(a[0])]}
    return fact   

"""facts = [
    {"functor": "borrowed", "arguments": ["u01", "i01", "185"]},
    {"functor": "user", "arguments": ["u01", "anna", "student"]}
]

for line in facts_to_prolog(facts):
    print(line)"""

#---Prolog Query Execution---


def run_query(fact_strings, goal):
    program = ":- consult('library.pl').\n" + "\n".join(fact_strings)
    with tempfile.NamedTemporaryFile("w", suffix=".pl", delete=False) as f:
        f.write(program)
        temp_path = f.name
    try:
        result = run([swipl_path, "-q", "-g", goal, "-t", "halt", temp_path],
                     capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        return False
    except FileNotFoundError:
        return False
    finally:
        os.remove(temp_path)
    return result.returncode == 0

def run_query_value(fact_strings,goal, value):
    program =":-consult('library.pl').\n" + "\n".join(fact_strings)
    with tempfile.NamedTemporaryFile("w",suffix=".pl",delete=False) as f:
        f.write(program)
        temp_path = f.name
    goal=f"{goal},write({value}),nl"
    try:
        result = run([swipl_path, "-q", "-g", goal, "-t", "halt", temp_path],
                     capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        return None
    finally:
        os.remove(temp_path)
    return result.stdout.strip()

def explain(reason):
    return REASONS.get(reason, f"Decision: {reason}")

"""print(run_query([], "is_rare(i15)."))              
print(run_query([], "may_borrow(u01, i06)."))        
print(run_query(facts_to_prolog([
    {"functor": "borrowed", "arguments": ["u04", "i16", "150"]}
]), "is_overdue(u04, i16)."))  """


#---JSON Extraction using LLM---

SYSTEM_PROMPT = '''You convert a library natural language query into JSON.
Output ONLY valid JSON in this exact shape:
{"facts": [{"functor": "...", "arguments": ["..."]}],
 "query": {"functor": "...", "arguments": ["..."]}}

Use the person's NAME exactly as written (e.g. "sara", "bob").
Use the book's full TITLE exactly as written (e.g. "the pragmatic programmer").
NEVER invent ids like u01 or i01. Use names and titles only.
All values MUST be lowercase.

Fact functors (conditions stated in the text):
- borrowed(Name, BookTitle, BorrowDay)   e.g. ["sara", "the pragmatic programmer", "170"]
- reserved(Name, BookTitle, Position)    e.g. ["bob", "deep learning", "1"]

Query functors (the question the sentence asks):
- is_overdue(Name, BookTitle)
- may_borrow(Name, BookTitle)
- is_available(BookTitle)
- is_rare(BookTitle)
- suggest_all(Name, Subject)             e.g. ["anna", "computer_science"]
- has_any_overdue(Name)                  e.g. ["bob"]

Examples:
Text: "Is the animal story available?"
JSON: {"facts": [], "query": {"functor": "is_available", "arguments": ["the animal story"]}}

Text: "Sara borrowed the pragmatic programmer on day 170. Is it overdue?"
JSON: {"facts": [{"functor": "borrowed", "arguments": ["sara", "the pragmatic programmer", "170"]}], "query": {"functor": "is_overdue", "arguments": ["sara", "the pragmatic programmer"]}}

Text: "Can Bob borrow artificial intelligence: a modern approach?"
JSON: {"facts": [], "query": {"functor": "may_borrow", "arguments": ["bob", "artificial intelligence: a modern approach"]}}

Text: "Suggest some history books for Clara."
JSON: {"facts": [], "query": {"functor": "suggest_all", "arguments": ["clara", "history"]}}
'''

def parse_sentence(sentence):
    prompt = SYSTEM_PROMPT + f'\nSentence: "{sentence}"\nOutput:'
    r = requests.post("http://localhost:11434/api/generate", json={
        "model": "qwen2.5:7b",
        "prompt": prompt,
        "stream": False,
        "format": "json"
    })
    return json.loads(r.json()["response"])

def query_to_goal(query):
    functor = query["functor"]
    args = ", ".join(query["arguments"])
    return f"{functor}({args})." 

"""result = extract_facts("Bob, a student, borrowed book i05 due on day 190.")
print(result)"""

#---Full Pipeline Connection---
def process(sentence):
    start = time.time()
    parsed = parse_sentence(sentence)
    print("PARSED:", parsed)
    try:
        resolved_facts = [resolve(f) for f in parsed["facts"]]            
        resolved_query = resolve(parsed["query"])
    except ValueError as e:
        elapsed = time.time() - start
        return elapsed, [], None, f"Error: {e}"
     

    fact_strings = facts_to_prolog(resolved_facts)
    goal = query_to_goal(resolved_query)

    if resolved_query["functor"]=="may_borrow":
        u,i=resolved_query["arguments"]
        reason=run_query_value(fact_strings,f"borrow_decision({u},{i},R)","R")
        answer=explain(reason)
    elif resolved_query["functor"]=="suggest_all":
        u, subject = resolved_query["arguments"]
        answer = run_query_value(fact_strings, f"suggest_all({u}, '{subject}', L)", "L")
    else:               
        result = run_query(fact_strings, goal)                    
        answer = "Yes." if result else "No."
    elapsed = time.time() - start
    return elapsed, fact_strings, goal, answer
