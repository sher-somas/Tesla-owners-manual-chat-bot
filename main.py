import uuid
from fastapi import FastAPI, HTTPException, Form
from fastapi import status as response_status
from pydantic import BaseModel
from app import invoke_chain
from dotenv import load_dotenv
from twilio.rest import Client
from fastapi import Body

load_dotenv()

twilio_client = Client()
app = FastAPI()

class Question(BaseModel):
    input_str : str

def send_message(llm_output):
    twilio_client.messages.create(from_="whatsapp:+14155238886",
                                        body=llm_output, to="whatsapp:+4915219432029")

@app.get("/")
def ping_check():
    return {"Hello": "World"}

@app.post("/question")
def translate(request: Question, status=response_status.HTTP_200_OK):
    
    try:
        llm_output = invoke_chain(request.input_str)
        # send_message(llm_output)
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

