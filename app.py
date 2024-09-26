from dotenv import load_dotenv
from langchain_community.vectorstores import Pinecone
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_openai import OpenAIEmbeddings
from langchain_together import ChatTogether
from pinecone import Pinecone as PineconeClient

load_dotenv()

llm = ChatTogether(temperature=0.0, model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")

index_name = "tesla-manuals"

pinecone_client = PineconeClient()
embeddings = OpenAIEmbeddings()
vector_store = Pinecone.from_existing_index(index_name=index_name, embedding=embeddings)
retriever = vector_store.as_retriever()


def invoke_chain(question: str) -> str:
    """
    Invokes a chain of operations to retrieve relevant information from the Pinecone vector store and generate an answer using the Meta-Llama 3.1 model.

    Args:
        question (str): The user's input question.

    Returns:
        str: The generated answer based on the retrieved context and question.

    Create a ChatPromptTemplate instance from the template
    prompt = ChatPromptTemplate.from_template(template)

    # Define a chain of operations using the RunnableParallel and RunnablePassthrough classes
    chain = (
        # Retrieve relevant context from the Pinecone vector store
        RunnableParallel({"context": retriever, "question": RunnablePassthrough()})

        # Apply the RAG prompt to the retrieved context and question
        | prompt

        # Use the Meta-Llama 3.1 model to generate an answer based on the applied prompt
        | ChatTogether(temperature=0, model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")

        # Parse the generated output as a string
        | StrOutputParser()
    )

    # Invoke the chain of operations and return the generated answer
    return chain.invoke(question)
    """

    template = """You are a Tesla car manual bot and have access to all the owner's manual of all the tesla car models ever produced.
    Answer the question with confidence and a friendly manner. If you don't know the answer, say I don't know.

    {context}
    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    # RAG
    model = ChatTogether(
        temperature=0, model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
    )

    chain = (
        RunnableParallel({"context": retriever, "question": RunnablePassthrough()})
        | prompt
        | model
        | StrOutputParser()
    )

    return chain.invoke(question)
