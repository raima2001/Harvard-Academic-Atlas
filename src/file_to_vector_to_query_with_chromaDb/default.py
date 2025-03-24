import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import AzureChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain.prompts import PromptTemplate
from configparser import ConfigParser
from uuid import uuid4
import requests, time, shutil, threading, tempfile
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
#from whisper_pine_cone import wisper_audio_to_transcript
import re
from langchain.indexes import VectorstoreIndexCreator
from PyPDF2 import PdfFileReader
from io import BytesIO
from docx import Document
from sentence_transformers import SentenceTransformer


# Functions to extract text
def extract_text_from_url(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, features="lxml")
        #print(' '.join(soup.text.split()))
        return ' '.join(soup.text.split())
    except Exception as e:
        print(f"Error fetching URL {url}: {str(e)}")
        return ''

"""
def extract_text_from_pdf(url):
    try:
        response = requests.get(url)
        pdf_reader = PdfFileReader(BytesIO(response.content))
        text = ''
        for page_num in range(pdf_reader.numPages):
            text += pdf_reader.getPage(page_num).extractText()
        return ' '.join(text.split())
    except Exception as e:
        print(f"Error fetching PDF from {url}: {str(e)}")
        return ''
    
def extract_text_from_docx(url):
    try:
        response = requests.get(url)
        doc = Document(BytesIO(response.content))
        text = ' '.join([p.text for p in doc.paragraphs])
        return ' '.join(text.split())
    except Exception as e:
        print(f"Error fetching DOCX from {url}: {str(e)}")
        return ''
"""
        
def extract_text_from_pdf(file_object):
    try:
        pdf_reader = PdfFileReader(file_object)
        text = ''
        for page_num in range(pdf_reader.numPages):
            text += pdf_reader.getPage(page_num).extractText()
        return ' '.join(text.split())
    except Exception as e:
        print(f"Error reading PDF from file object: {str(e)}")
        return ' '
    
def extract_text_from_docx(file_object):
    try:
        doc = Document(file_object)
        text = ' '.join([p.text for p in doc.paragraphs])
        return ' '.join(text.split())
    except Exception as e:
        print(f"Error reading DOCX from file object: {str(e)}")
        return ''
    
def save_text_to_file(text, file_name, directory_path):
    os.makedirs(directory_path, exist_ok=True)
    file_name_with_extension = file_name + '.txt' # Adding .txt extension
    with open(os.path.join(directory_path, file_name_with_extension), 'w', encoding='utf-8') as f:
        f.write(text)

def process_url(url, file_name_location):
    try:
        #extract text from URL
        text = extract_text_from_url(url)
        
        # Extracting the file name without extension and appending "multisearch"
        base_file_name = os.path.basename(url).split('.')[0] + "_multisearch"
        file_name = base_file_name
        file_name_with_extension = file_name + '.txt'  # Adding .txt extension
        counter = 1
        
        # Check if file_name already exists, if so, rename it uniquely
        while os.path.exists(os.path.join(file_name_location, file_name_with_extension)):
            file_name = base_file_name + f"_{counter}"
            file_name_with_extension = file_name + '.txt'
            counter += 1

        save_text_to_file(text, file_name, file_name_location) # Saving the text as a .txt file

    except Exception as e:
        print(f"Error processing URL {url}: {str(e)}")

    
def process_file(file_attached, file_name_location):

    """
    with open(file_attached, 'rb') as file:
        if file_attached.endswith('.pdf'):
            text = extract_text_from_pdf(file)
        elif file_attached.endswith('.docx'):
            text = extract_text_from_docx(file)
    """

    try:
        if file_attached.endswith('.pdf'):
            text = extract_text_from_pdf(file_attached)
        elif file_attached.endswith('.docx'):
            text = extract_text_from_docx(file_attached)
        else:
            print("file is not .pdf or .docx")
            text = " "
        
        # Extracting the file name without extension and appending "multisearch"
        base_file_name = os.path.basename(file_attached).split('.')[0] + "_multisearch"
        file_name = base_file_name
        file_name_with_extension = file_name + '.txt'  # Adding .txt extension
        counter = 1
        
        # Check if file_name already exists, if so, rename it uniquely
        while os.path.exists(os.path.join(file_name_location, file_name_with_extension)):
            file_name = base_file_name + f"_{counter}"
            file_name_with_extension = file_name + '.txt'
            counter += 1

        save_text_to_file(text, file_name, file_name_location) # Saving the text as a .txt file

    except Exception as e:
        print(f"Error processing File {file_attached}: {str(e)}")


def create_pdfsearch(links, files_array, collection_name, file_name_location):
 
    for url in links:
        process_url(url, file_name_location)

    for file_attached in files_array:
        process_file(file_attached, file_name_location)

    loader = DirectoryLoader(file_name_location)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100, separators=[" ", ",", "\n"])
    documents = text_splitter.split_documents(documents)

    embeddings = SentenceTransformer('sentence-transformers/paraphrase-MiniLM-L6-v2')
    #response = model.encode(docx_text)
    
    #embeddings = OpenAIEmbeddings(
    #    deployment="text-embedding-pinecone",
    #    model="text-embedding-ada-002",
    #    chunk_size=1
    #)

    persist_directory = 'db'

    
    pdfsearch = Chroma.from_documents(
        documents,
        embeddings,
        collection_name=collection_name,
        persist_directory=persist_directory
    )

    pdfsearch.persist()

    return pdfsearch


def delete_vector_after_one_hour(persist_directory, collection_name):
    time.sleep(1800)  # Wait for 30min (1800 seconds)
    chroma_db_path = os.path.join(persist_directory, collection_name)
    try:
        if os.path.exists(chroma_db_path):
            shutil.rmtree(chroma_db_path)
            print(f"Successfully deleted ChromaDB vector {collection_name}.")
        else:
            print(f"Path does not exist, cannot delete ChromaDB vector {collection_name}: {chroma_db_path}")
    except Exception as e:
        print(f"Error deleting ChromaDB vector {collection_name}: {str(e)}")


def delete_directory_after_one_hour(directory_path):
    time.sleep(1800)  # Wait for 30min (1800 seconds)
    try:
        shutil.rmtree(directory_path)
        print(f"Successfully deleted directory {directory_path}.")
    except Exception as e:
        print(f"Error deleting directory {directory_path}: {str(e)}")
        

def article_paragraph(collection_name, query):
    persist_directory = 'db'
    embedding = SentenceTransformer('sentence-transformers/paraphrase-MiniLM-L6-v2')

    #embedding = OpenAIEmbeddings(
    #    deployment=deployment,
    #    model=model,
    #    chunk_size=1
    #)
    
    vectordb = Chroma(persist_directory=persist_directory, 
                      collection_name=collection_name,
                      embedding_function=embedding)
    
    retriever = vectordb.as_retriever()
    llm =  AzureChatOpenAI(
        deployment_name=deployment_name,
        temperature=0,
        openai_api_base=openai_api_base,
        openai_api_key=openai_api_key,
        openai_api_type=openai_api_type,
        openai_api_version=openai_api_version"
    )
    
    # Create a prompt template with input variables for the context and question
    prompt_template = """Imagine you are a seasoned academic advisor and course planning expert specializing in personalized student recommendations for academic success. Your task is to craft an in-depth, detailed paragraph of a minimum of 400 words, focusing primarily on the given subtopic while seamlessly integrating the context of personalized course recommendations and academic scheduling. Emphasize the role of personalized course planning tools in helping students balance workloads, manage schedules, and align their choices with academic and career goals. Avoid including introductions or conclusions unless specified in the subtopic.
    {context}

    Question: {question}
    Answer :"""
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )

    # Use the RetrievalQA to create a question-answering chain based on the prompt
    qa = RetrievalQA.from_chain_type(llm=llm,
                                     chain_type="stuff", 
                                     retriever=retriever,
                                     chain_type_kwargs={"prompt": prompt}
                                     )
    
    # Run the chain with the given context as input
    result = qa.run(query)
    return result

def article_creation_with_outline(links, files_array, query, article_outline):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name_location = f"extracted_texts_{query.replace(' ', '_')}_{timestamp}"

    # Ensure the directory exists
    os.makedirs(file_name_location, exist_ok=True)

    unique_id = str(uuid4())[:8]  # unique identifier to avoid overlapping
    collection_name = query.replace(" ", "_") + "_" + timestamp + "_" + unique_id
    pdfsearch = create_pdfsearch(links, files_array, collection_name, file_name_location)

    # Update the article outline with the topic name
    article_outline = [f"{outline} (Under the Topic: {query})" for outline in article_outline]

    article = ''

    # Loop through each section of the outline and generate paragraphs
    for data in article_outline:
        article_para = article_paragraph(collection_name, data)
        article += data.strip()
        article += '\n'
        article += article_para.strip()
        article += '\n\n'

    # Save the final article in a text file
    try:
        with open(f'article_on_{query}.txt', 'w') as f:
            f.write(article)
        print(f'article on {query} is done')

        # Schedule deletion of ChromaDB vector after one hour
        threading.Thread(target=delete_vector_after_one_hour, args=('db', collection_name)).start()
        # Schedule deletion of file_name_location directory after one hour
        threading.Thread(target=delete_directory_after_one_hour, args=(file_name_location,)).start()
        
    except Exception as e:
        print(f"Error saving article: {str(e)}")

