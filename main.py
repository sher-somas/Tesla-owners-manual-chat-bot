from fastapi import FastAPI, HTTPException
from fastapi import status as response_status
from pydantic import BaseModel
from app import invoke_chain
from whatsapp import send_message
from fastapi import Body


app = FastAPI()

class Question(BaseModel):
    input_str : str


@app.get("/")
def ping_check():
    return {"Hello": "World"}

@app.post("/question")
def translate(request: Question, status=response_status.HTTP_200_OK):
    
    try:
        llm_output = invoke_chain(request.input_str)
        return {"response": llm_output}
    except Exception as e:
        raise HTTPException(status_code=response_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/question/whatsapp")
def translate(request: str = Body(..., media_type="application/json"), status=response_status.HTTP_200_OK):
    
    message = request.lower()
    try:
        llm_output = invoke_chain(message)
        send_message(llm_output)
        return {"response": llm_output}
    except Exception as e:
        raise HTTPException(status_code=response_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

