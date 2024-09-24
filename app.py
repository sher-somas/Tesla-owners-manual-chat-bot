from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from pinecone import Pinecone as PineconeClient
from langchain_community.vectorstores import Pinecone

from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_together import ChatTogether
from twilio.twiml.messaging_response import MessagingResponse
from flask import Flask, request

load_dotenv()

app = Flask(__name__)

llm = ChatTogether(temperature=0.0, model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")


index_name = 'tesla-manuals'

pinecone_client = PineconeClient()
embeddings = OpenAIEmbeddings()
vector_store = Pinecone.from_existing_index(index_name=index_name, embedding=embeddings)
retriever = vector_store.as_retriever()

# RAG prompt
template = """You are a Tesla car manual bot and have access to all the owner's manual of all the tesla car models ever produced.
Answer the question with confidence and a friendly manner. If you don't know the answer, say I don't know.

{context}
Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

# RAG
model = ChatTogether(temperature=0, model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")

chain = (
    RunnableParallel({"context": retriever, "question": RunnablePassthrough()})
    | prompt
    | model
    | StrOutputParser()
)

print(chain.invoke("what is ludacris mode"))


# Route to test if server is running
@app.route("/ping", methods=['GET'])
def pinger():
    return "<p>Hello world!</p>"

# Route to answer queries based on the document embeddings
@app.route('/answer', methods=['POST'])
def answer():
    query = request.form.get('Body')  # Get the JSON data from the request body
    result = chain.invoke(query)
    print(result)
    resp = MessagingResponse()
    msg = resp.message()
    msg.body(result)
    return str(resp)

if __name__ == '__main__':
    app.run(port=8091)