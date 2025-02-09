#Start  - uvicorn main:app --host 0.0.0.0 --reload
#
#

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def home() -> list:
    #return {"data": "message"}
    return "Hello"
    #return [1 , 2]


@app.get("/param/")
async def items(id) -> list:
    return f"answer-{id}"