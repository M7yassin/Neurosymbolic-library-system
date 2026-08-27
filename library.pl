:- dynamic borrowed/3.
:- dynamic reserved/3.

user(u01, anna,  student).
user(u02, bob,   student).
user(u03, clara, staff).
user(u04, adam,   professor).
user(u05, sara,    professor).

borrow_limit(student, 3).
borrow_limit(staff, 5).
borrow_limit(professor, 10).

book(i01, 'introduction to algorithms', manual, 1990 , computer_science).
book(i02, 'art of prolog', manual, 1986 , computer_science).
book(i03, 'deep learning', manual, 2016 , computer_science).
book(i04, 'pragmatic programmer', manual, 2019 , computer_science).
book(i05, 'artificial intelligence: a modern approach', manual, 1995 , computer_science).
book(i06, 'sapiens: a brief history of humankind', monograph, 2011 , history).
book(i07, 'silk roads: a new history of the world', monograph, 2015 , history).
book(i08,'thinking, fast and slow', monograph, 2011 , psychology).
book(i09, 'power of habit', monograph, 2012 , psychology).
book(i10,'educated: a memoir', monograph, 2018 , biography).
book(i11,'name of the rose', monograph, 1980 , literature).
book(i12, 'klara and the sun', monograph, 2021 , literature).
book(i13,'kafka on the shore', monograph, 2002 , literature).
book(i14,'da vinci code', monograph, 2003 , literature).
book(i15,'divine comedy', monograph, 1320 , literature).
book(i16,'a brief history of time', monograph, 1988 , physics).
book(i17,'elegant universe', monograph, 1999 , physics).
book(i18,'feynman lectures on physics', monograph, 1964 , physics).
book(i19,'selfish gene', monograph, 1976 , biology).
book(i20,'origin of species', monograph, 1859 , biology).
book(i21,'oxford english dictionary', reference, 1884 , language).
book(i22,'merriam-webster dictionary', reference, 1961 , language).
book(i23,'math: the language of the universe', monograph, 2019 , mathematics).
book(i24,'space: the final frontier', monograph, 2020 , astronomy).
book(i25,'universe in a nutshell', monograph, 2001 , astronomy).

today(200).

borrow_period(30).

borrowed(u01, i02, 169).

reserved(u02, i01, 1).   
reserved(u03, i01, 2).    
reserved(u04, i01, 3).    
reserved(u02, i06, 1).
reserved(u04, i16, 1).

is_rare(I):-
    book(I, _, _, Y, _),
    Y < 1915.

is_overdue(U, I):-
    borrowed(U, I, D),
    borrow_period(P),
    L is D + P,
    today(T),
    T > L.

borrow_count(U, C):-
    findall(X, borrowed( U, X, _), L),
    length(L, C).
    

reach_borrow_limit(U):-
    user(U, _, R),
    borrow_limit(R, L),
    borrow_count(U, C),
    C >= L.

has_any_overdue(U):-
    borrowed(U, I, _),
    is_overdue(U, I).

blocked(U):-reach_borrow_limit(U).
blocked(U):-has_any_overdue(U).
  
is_available(I):-
    book(I, _, Type, _, _),
    Type \= reference,
    \+ borrowed(_,I,_),
    \+ reserved(_,I,_).

reserve(U,I):-
    user(U, _, _),
    book(I, _, _, _, _),
    is_available(I).

overdue_books(U, L):-
    findall(I, is_overdue(U, I), L).

remaining_borrow_days(U, D):-
    user(U,_,R),
    borrow_limit(R, Max),
    borrow_count(U, C),
    D is Max - C.

queue_length(I, C):-
    findall(X, reserved(X, I, _), L),
    length(L, C).

next_in_line(I, U) :-
    reserved(U, I, P),
    \+ ( reserved(_, I, Q), Q < P ).

ahead_in_queue(U1, U2, I) :-
    reserved(U1, I, P1),
    reserved(U2, I, P2),
    P2 =:= P1 + 1.

ahead_in_queue(U1, U2, I) :-
    reserved(U1, I, P1),
    reserved(U3, I, P3),
    P3 =:= P1 + 1,
    ahead_in_queue(U3, U2, I).

reservation_allows(_, I) :- \+ reserved(_, I, _).  
reservation_allows(U, I) :- next_in_line(I, U).

reserved_by_other(U, I) :-
    reserved(Other, I, _),
    Other \= U.

may_borrow(U,I):-
    user(U, _, _),
    book(I, _, Type, _, _),
    Type \= reference,
    reservation_allows(U, I),
    \+ is_rare(I),
    \+ blocked(U),
    \+ borrowed(_,I,_).

suggest(U, Subject, I) :-
    book(I, _, _, _, Subject),
    is_available(I),
    may_borrow(U, I).

suggest_all(U, Subject, List) :-
    findall(book(I, Title, Type, Year, Subject),
            ( suggest(U, Subject, I),
              book(I, Title, Type, Year, Subject) ),
            List).

add_borrow(U, I) :-
    may_borrow(U, I),
    today(T),
    assertz(borrowed(U, I, T)).

add_reservation(U, I) :- 
    user(U, _, _),
    book(I, _, _, _, _),
    \+ is_available(I),
    \+ reserved(U, I, _),          
    queue_length(I, N),
    NextRes is N + 1,
    assertz(reserved(U, I, NextRes)).

borrow_decision(U, I, allowed) :-
    may_borrow(U, I), !.
borrow_decision(U, I, reference_book) :-
    book(I, _, reference, _, _), !.
borrow_decision(U, I, rare_book) :-
    is_rare(I), !.
borrow_decision(U, I, over_limit) :-
    reach_borrow_limit(U), !.
borrow_decision(U, I, has_overdue) :-
    has_any_overdue(U), !.
borrow_decision(U, I, already_borrowed) :-
    borrowed(_, I, _), !.
borrow_decision(U, I, reserved_by_other) :-
    reserved_by_other(U, I), !.
borrow_decision(_, _, unknown_reason).
