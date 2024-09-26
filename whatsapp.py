from twilio.rest import Client
from dotenv import load_dotenv

twilio_client = Client()
load_dotenv()

def send_message(llm_output):
    twilio_client.messages.create(from_="whatsapp:+14155238886",
                                        body=llm_output, to="whatsapp:<>") # add your phone number here with the country code and remove <>
