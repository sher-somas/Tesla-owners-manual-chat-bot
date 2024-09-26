from fastapi import Body, FastAPI, HTTPException
from fastapi import status as response_status
from pydantic import BaseModel

from app import invoke_chain
from whatsapp import send_message

app = FastAPI(
    title="Tesla owner's manual WhatApp Chatbot",
    version="0.0.1",
    contact={
        "name": "Shreyas Somashekar",
        "email": "sher.somas@gmail.com",
    },
)


class Question(BaseModel):
    input_str: str


@app.get("/")
def ping_check():
    """
    Endpoint to handle GET requests to the root URL ("/"), returning a simple "Hello World" response.

    Returns:
        dict: A dictionary containing the greeting message.
    """
    return {"Hello": "World"}


@app.post("/question")
def web_request(request: Question, status=response_status.HTTP_200_OK):
    """
    Web-based question answering endpoint to handle POST requests containing user input.

    Args:
        request (Question): A Question object containing the user's input string.

    Returns:
        dict: A dictionary containing the translated output from the LLM.

    Raises:
        HTTPException: If an error occurs during processing, returns a 500 Internal Server Error response with the exception details.

    Notes:
        This endpoint is designed for handling web-based requests. It takes user input as a string, translates it using the LLM, and returns the result in JSON format.
    """
    try:
        llm_output = invoke_chain(request.input_str)
        return {"response": llm_output}
    except Exception as e:
        raise HTTPException(
            status_code=response_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.post("/question/whatsapp")
def whatsapp_request(
    request: str = Body(..., media_type="application/json"),
    status=response_status.HTTP_200_OK,
):
    """
    WhatsApp messaging endpoint to handle POST requests containing user input.

    Args:
        request (str): The user's input string as a JSON payload.

    Returns:
        dict: A dictionary containing the translated output from the LLM and sent to WhatsApp.

    Raises:
        HTTPException: If an error occurs during processing, returns a 500 Internal Server Error response with the exception details.

    Notes:
        This endpoint is designed for sending automated messages via WhatsApp. It takes user input as a string, translates it using the LLM, and sends the result to WhatsApp using the `send_message` function.
    """
    message = request.lower()
    try:
        llm_output = invoke_chain(message)
        send_message(llm_output)
        return {"response": llm_output}
    except Exception as e:
        raise HTTPException(
            status_code=response_status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
