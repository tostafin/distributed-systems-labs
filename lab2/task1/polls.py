from fastapi import FastAPI
from typing import List
from dataclasses import dataclass

app = FastAPI()

"""
1. Resources: polls and votes
2. Containment Relationship:
poll
├── {id1}
│   └── vote
│       ├── {id4}
│       └── {id5}
├── {id2}
└── {id3}

+----------------------+-----+-----+------+--------+
|                      | GET | PUT | POST | DELETE |
+----------------------+-----+-----+------+--------+
| /poll                |  Y  |  N  |  Y   |   N    |
| /poll/{id}           |  Y  |  Y  |  N   |   Y    | 
| /poll/{id}/vote      |  Y  |  N  |  Y   |   N    |
| /poll/{id}/vote/{id} |  Y  |  Y  |  N   |   ?    |
+----------------------+-----+-----+------+--------+
Y = yes
N = no
? = maybe yes, maybe no (in our case yes)

3. URIs embed IDs of "child" instance resources
4. POST on the container is used to create child resources
5. PUT/DELETE for updating and removing child resources
"""


@dataclass
class Answer:
    answer: str
    cnt: int = 0


@dataclass
class Poll:
    question: str
    answers: List[Answer]


polls: List[Poll] = [
    Poll("Kiedy piwo?", [
        Answer("Dziś"),
        Answer("Jutro")
    ]),
    Poll("Kiedy jedzenie?", [
        Answer("Pojutrze"),
        Answer("Popojutrze"),
        Answer("Nigdy :(")
    ])
]


@app.get("/poll")
async def get_poll():
    return polls


@app.post("/poll")
async def post_poll(poll: Poll):
    polls.append(poll)
    return poll


@app.get("/poll/{poll_id}")
async def get_poll_id(poll_id: int):
    return polls[poll_id]


@app.put("/poll/{poll_id}")
async def put_poll_id(poll_id: int, poll: Poll):
    polls[poll_id] = poll
    return polls[poll_id]


@app.delete("/poll/{poll_id}")
async def delete_poll_id(poll_id: int):
    return polls.pop(poll_id)


@app.get("/poll/{poll_id}/vote")
async def get_poll_id_vote(poll_id: int):
    return polls[poll_id].answers


@app.post("/poll/{poll_id}/vote")
async def post_poll_id_vote(poll_id: int, answer: Answer):
    polls[poll_id].answers.append(answer)
    return polls[poll_id].answers


@app.get("/poll/{poll_id}/vote/{vote_id}")
async def get_poll_id_vote_id(poll_id: int, vote_id: int):
    return polls[poll_id].answers[vote_id].cnt


@app.put("/poll/{id}/vote/{id_vote}")
async def put_poll_id_vote_id(poll_id: int, vote_id: int):
    polls[poll_id].answers[vote_id].cnt += 1
    return polls[poll_id].answers[vote_id].cnt


@app.delete("/poll/{id}/vote/{id_vote}")
async def delete_poll_id_vote_id(poll_id: int, vote_id: int):
    polls[poll_id].answers[vote_id].cnt -= 1
    return polls[poll_id].answers[vote_id].cnt
