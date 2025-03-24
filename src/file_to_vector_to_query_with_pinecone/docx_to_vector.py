import pinecone, openai, time
from docx import Document
import hashlib
from sentence_transformers import SentenceTransformer

openai.api_type = openai.api_type
openai.api_base = openai.api_base
openai.api_version = openai.api_version
openai.api_key = openai.api_key
vector_engine_name = vector_engine_name
turbo_engine_name = turbo_engine_name

# Initialize Pinecone
pinecone.init(api_key=api_key, environment="asia-southeast1-gcp-free")
index = pinecone.Index('connections')

def get_embedding(docx_text):
    while True:
        try:
            model = SentenceTransformer('sentence-transformers/paraphrase-MiniLM-L6-v2')
            response = model.encode(docx_text)
            embeds = response['data'][0]['embedding'] # Extracting the embedding list
            return embeds
        except Exception as e:
            print(f"Connection error: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)

def split_text_into_lines(text, max_line_length=150):
    lines = []
    words = text.split()
    line = ""
    for word in words:
        if len(line) + len(word) + 1 > max_line_length:
            lines.append(line.strip())
            line = ""
        line += word + " "
    lines.append(line.strip())
    return lines

# Read the lines from the .docx file
def read_docx_lines(file):
    try:
        doc = Document(file)
        text = " ".join(paragraph.text for paragraph in doc.paragraphs)
        lines = split_text_into_lines(text)
    except FileNotFoundError:
        print(f"The file {file} was not found.")
    except PermissionError:
        print(f"You don't have permission to read the file {file}.")
    except Exception as e:
        print(f"An unexpected error occurred while reading the file {file}: {e}")
    return lines

# Generates an ID from the .docx file
def generate_id_from_file(file):
    try:
        lines = read_docx_lines(file)
        content = '\n'.join(lines)
        file_hash = hashlib.sha256(content.encode())
        print("docx_id original =", file_hash.hexdigest())
        return file_hash.hexdigest()
    except Exception as e:
        print(f"An error occurred while generating the ID for the file: {e}")
        return None

# Check if the .docx file exists in Pinecone
def check_if_docx_exists_in_pinecone(file):
    try:
        docx_id = generate_id_from_file(file)
        namespace = docx_id
        lines = read_docx_lines(file)
        line_ids = [hashlib.sha256(line.encode()).hexdigest() for line in lines]  # Vector IDs for every line

        # Fetch the vectors with the given line IDs from Pinecone
        response = index.fetch(ids=line_ids, namespace=namespace)
        
        # Return False if there are no keys, otherwise return True
        return len(response['vectors'].keys()) != 0
    
    except Exception as e:
        print(f"Error while checking docx existence in Pinecone: {e}")
        return False

# Deletes the .docx file from Pinecone
def delete_docx_from_pinecone(file):
    try:
        docx_id = generate_id_from_file(file) 
        namespace = docx_id
        lines = read_docx_lines(file)
        line_ids = [hashlib.sha256(line.encode()).hexdigest() for line in lines]  # Vector IDs for every line

        # Delete the vectors with the given line IDs from Pinecone
        response = index.delete(ids=line_ids, namespace=namespace)

    except Exception as e:
        print(f"Error while deleting docx from Pinecone: {e}")

# Processes the .docx file
def process_docx(file):
    docx_id = generate_id_from_file(file)
    namespace = docx_id  # Set the namespace to be the generated ID from the file
    print(f"Processing DOCX in namespace: {namespace}")

    if check_if_docx_exists_in_pinecone(file):
        print("DOCX already exists in Pinecone.")
        return

    lines = read_docx_lines(file) # Splitting the text by newline characters
    to_upsert = []
    for line in lines:
        line_id = hashlib.sha256(line.encode()).hexdigest() # Create an ID for each line
        line_embedding = get_embedding(line)
        metadata = {"text": line}
        to_upsert.append({"id": line_id, "values": line_embedding, "metadata": metadata})

    if to_upsert:
        index.upsert(vectors=to_upsert, namespace=namespace)
        print("Ingesting DONE.")
    else:
        print("No vectors to upsert.")

def query_docx(text_query, namespace, top_k=12):
    try:
        query_embedding = get_embedding(text_query)
        response = index.query(queries=[query_embedding], include_metadata=True, namespace=namespace, top_k=top_k)
        
        matches = response['results'][0]['matches']
        docx_texts = [match['metadata']['text'] for match in matches]  # Adjust this line according to the correct structure
        return docx_texts
      
    except Exception as e:
        print(f"Error while querying docx: {e}")
        return []


def conversation_model(text_query, namespace):
    # Query Pinecone to get top matching docx texts
    docx_texts = query_docx(text_query, namespace)

    # Construct the Pinecone answer string
    pinecone_answer = ' '.join(docx_texts)

    # Create the conversation prompt
    main_prompt = """
    Act as a helpful and knowledgeable academic advisor with strong conversational skills. Provide clear, concise, and well-informed responses related to the Harvard Academia Atlas, particularly with respect to course planning and academic success for Harvard Law School students. Avoid using vague or indefinite expressions.
    <|im_end|>
    <|im_start|>user
    Question: What are some ways Harvard Law School students can balance academic workload with extracurricular activities?
    Answer: 
    The Harvard Academia Atlas offers personalized course recommendations that help students create conflict-free schedules, enabling them to balance academic requirements with extracurricular activities. By considering course load, scheduling conflicts, and workload distribution, the tool simplifies the process of managing both academics and extracurriculars effectively.
    <|im_end|>
    <|im_start|>assistant
    Managing both academics and extracurriculars at Harvard Law School can be challenging, but the Harvard Academia Atlas helps by providing tailored course suggestions that fit your academic and career goals. It takes into account scheduling conflicts and workload distribution, making it easier to prioritize both studies and extracurricular commitments.
    <|im_end|>
    <|im_start|>user
    Question : {text_query}
    Answer :
    {pinecone_answer}
    <|im_end|>
    <|im_start|>assistant
    """.format(text_query=text_query,pinecone_answer= pinecone_answer)

    # Query the GPT-3.5 model with the constructed prompt - Replace with Llama
    response = openai.Completion.create(
        engine=turbo_engine_name,
        prompt=main_prompt,
        temperature=0,
        max_tokens=500,
        top_p=0.5,
        stop=["<|im_end|>"])

    return response['choices'][0]['text']


def interact_with_user():
    while True:
        action = input("What would you like to do? Type 'query', 'delete', 'change', or 'exit': ")

        if action.lower() == "exit":
            break
        elif action.lower() == "delete":
            delete_file_name = input("Please enter the file name (in the same directory) to delete: ")
            with open(delete_file_name, 'rb') as delete_file:
                delete_docx_from_pinecone(delete_file)
                print(f"File {delete_file_name} has been deleted from Pinecone.")
            continue
        elif action.lower() == "query" or action.lower() == "change":
            file_name = input("Please enter the file name (in the same directory): ")

            with open(file_name, 'rb') as file:
                # Check if the docx file has already been ingested
                if check_if_docx_exists_in_pinecone(file):
                    print("File already ingested.")
                else:
                    print("File is not ingested. Ingesting now...")
                    process_docx(file)
                    print("File is now ingested.")

                # Get the docx's unique ID
                namespace = generate_id_from_file(file)

                # Query loop
                while action.lower() == "query":
                    text_query = input("Please enter your question or type 'change' to switch file: ")
                    if text_query.lower() == "change":
                        break
                    response_text = conversation_model(text_query, namespace)
                    print(response_text)
        else:
            print("Invalid choice. Please try again.")

interact_with_user()
