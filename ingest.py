
import glob
from tqdm import tqdm
from dotenv import load_dotenv
from argparse import ArgumentParser
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI



def list_pdfs(args):
    """
    This function will return all the pdf from the folder mentioned. 
    """
    list_of_pdfs = glob.glob(args.folder_name + "/*.pdf")
    return list_of_pdfs


def load_pdfs(list_of_pdfs):
    """
    Given a list of pdfs load it using the PyPDFLoader
    """
    docs = []

    for pdf in tqdm(list_of_pdfs, desc=f'loading pdfs...'):
        load_pdf = PyPDFLoader(pdf, extract_images=False)
        docs.extend(load_pdf.load())

    return docs


def get_chunks_from_pdfs(docs):
    """
    This function while chunk the input docs and return the chunks
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 800,  
                                                   chunk_overlap = 200, 
                                                   separators=["\n\n","\n",".","\%d\n"])  
    
    chunks = text_splitter.split_documents(docs)

    return chunks


def get_openai_embedding(text, openai_client):
    response = openai_client.embeddings.create(
        input=[text],
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding


def initialize_pinecone(index_name: str):
    """
    Initialize pinecone client and list all the indexes. 

    if the index we are looking for is not present, then create the index and return the pinecone client
    """
    pinecone_client = Pinecone()
    existing_indexes = []

    for indexes in pinecone_client.list_indexes():
       
        existing_indexes.append(indexes["name"])

    if index_name not in existing_indexes:
        pinecone_client.create_index(index_name, dimension=1536, 
                                    spec=ServerlessSpec(cloud='aws',
                                                        region='us-east-1'))
    
    return pinecone_client


def upload_chunks_to_pinecone(chunks, index_name):

    pinecone_client = initialize_pinecone(index_name)
    openai_client = OpenAI()

    for i, chunk in tqdm(enumerate(chunks),desc="uploading to pinecone"):
        response = openai_client.embeddings.create(input=chunk.page_content,
                                                   model="text-embedding-ada-002",
                                                   encoding_format="float")
        embedding = response.data[0].embedding
        pinecone_index = pinecone_client.Index(index_name)
        pinecone_index.upsert(vectors=[(f"chunk-{i}", embedding, {"chunk": chunk.page_content})], namespace='manual')
        

def query_pinecone(pinecone_client,openai_client, query_sample):

    query_embedding = get_openai_embedding(query_sample, openai_client)
    pinecone_index = pinecone_client.Index('tesla-manuals')
    result = pinecone_index.query(namespace='manual',vector=query_embedding, top_k=5, include_metadata=True )
    return result

if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--folder_name", type=str, default='manuals', help="Folder containing the manuals")
    args = parser.parse_args()
    
    load_dotenv()
    openai_client =OpenAI()
    
    print("-" * 30, "loading pdfs", "-" * 30, "\n")
    list_of_pdfs = list_pdfs(args)
    loaded_pdfs = load_pdfs(list_of_pdfs)

    print("-" * 30, "creating chunks", "-" * 30, "\n")
    chunks = get_chunks_from_pdfs(loaded_pdfs)
    
    print("-" * 30, "uploading chunks to pinecone", "-" * 30, "\n")
    upload_chunks_to_pinecone(chunks, 'tesla-manuals')
    
    pinecone_client = initialize_pinecone('tesla-manuals')
    query = "explain ludacrious mode"
    query_pinecone(pinecone_client, openai_client, query)
    