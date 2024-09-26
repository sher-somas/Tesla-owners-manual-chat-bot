from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from pinecone import Pinecone as PineconeClient
from langchain_community.vectorstores import Pinecone
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_together import ChatTogether



load_dotenv()

llm = ChatTogether(temperature=0.0, model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")

index_name = 'tesla-manuals'

pinecone_client = PineconeClient()
embeddings = OpenAIEmbeddings()
vector_store = Pinecone.from_existing_index(index_name=index_name, embedding=embeddings)
retriever = vector_store.as_retriever()

def invoke_chain(question):
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


    return chain.invoke(question)
