from pipeline import process

sentences = ["is the sapiens: a brief history of humankind available?",
"bob has borrowed i02 on day 169 , Is it overdue?",
"sara borrowed the pragmatic programmer on day 170. Is it overdue?",
"clara wants to borrow i03. May she borrow it?",
"clara wants to borrow the oxford english dictionary. May she borrow it?",
"sara wants to borrow i20. is it able to be borrowed?",
"bob borrowe 3 books: i01 and i05 and i13 on day 180, and he wants to borrow i24,could he borrow it ?",
"bob borrowed i01 on day 150. Can he borrow deep learning?",
"clara wants to borrow i01 which is borrowed by bob on day 170.Is the book overdue and Is she able to borrow it?",
"suggest computer science books for adam",
"bob borrowed i02 on d ay 170 and sara borrowed i04 on day 170. Suggest computer science books for adam.",
"bob borrowed 3 books: i01 and i05 and i13 on day 180, and he wants to borrow i10 ,could he borrow it ?",
"Can sara borrow the theory of everything?",
"Can michael borrow deep learning?",
]

for sentence in sentences:
    time, facts, goal, answer = process(sentence)
    print("SENTENCE:",sentence)
    print(f"Time taken for processing: {time:.2f} seconds")
    print("Facts:", facts)
    print("Goal:", goal)
    print("Answer:", answer)
    print()


"""
Is sapiens available?

bob has borrowed i02 on day 169 , Is it overdue?

sara borrowed the pragmatic programmer on day 170. Is it overdue?

clara wants to borrow i03. May she borrow it?

clara wants to borrow the oxford english dictionary. May she borrow it?

sara wants to borrow i20. is it able to be borrowed?

bob borrowe 3 books: i01 and i05 and i13 on day 180, and he want to borrow i15,could he borrow it ?

bob borrowed i01 on day 150. Can he borrow deep learning?

clara wants to borrow i01 which is borrowed by bob on day 170.Is the book overdue and Is she able to borrow it?

suggest computer science books for adam

bob borrowed i02 on d ay 170 and sara borrowed i04 on day 170. Suggest computer science books for adam.

bob borrowed 3 books: i01 and i05 and i13 on day 180, and he wants to borrow i10 ,could he borrow it ?

Can sara borrow the theory of everything?

Can michael borrow deep learning?
"""
