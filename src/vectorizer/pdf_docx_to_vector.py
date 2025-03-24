import pinecone, openai, time
from PyPDF2 import PdfReader
import hashlib
from docx import Document

# Initialize Pinecone
openai.api_type = openai.api_type
openai.api_base = openai.api_base
openai.api_version = openai.api_version
openai.api_key = openai.api_key
vector_engine_name = vector_engine_name
turbo_engine_name = turbo_engine_name

# Initialize Pinecone
pinecone.init(api_key=api_key, environment="asia-southeast1-gcp-free")
index = pinecone.Index('connections')

# Fetch embeddings from OpenAI service
def get_embedding(text):
    while True:
        try:
            # Request to get the embedding
            response = openai.Embedding.create(engine=vector_engine_name, input=[text])
            embeds = response['data'][0]['embedding']
            return embeds
        except Exception as e:
            print(f"Connection error: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)

# Split large text into smaller lines for Docx
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

# Read either docx or pdf files
def read_file_lines(file, file_type):
    try:
        if file_type == "docx":
            doc = Document(file)
            text = " ".join(paragraph.text for paragraph in doc.paragraphs)
            lines = split_text_into_lines(text)
        elif file_type == "pdf":
            pdf_reader = PdfReader(file)
            lines = []
            for page_num in range(len(pdf_reader.pages)):
                page_text = pdf_reader.pages[page_num].extract_text()
                lines.extend(page_text.splitlines())

        return lines
    
    except FileNotFoundError:
        print(f"The file {file} was not found.")
    except PermissionError:
        print(f"You don't have permission to read the file {file}.")
    except Exception as e:
        print(f"An unexpected error occurred while reading the file {file}: {e}")
    return lines

# Generate a unique identifier for a given file (namespace)
def generate_id_from_file(file, file_type):
    try:
        lines = read_file_lines(file, file_type)
        content = '\n'.join(lines)
        file_hash = hashlib.sha256(content.encode())
        return file_hash.hexdigest()
    except Exception as e:
        print(f"An error occurred while generating the ID for the file: {e}")
        return None

# Check if the file already exists in Pinecone
def check_if_file_exists_in_pinecone(file, file_type):
    try:
        file_id = generate_id_from_file(file, file_type)
        print("namespace at check_if_file_exists_in_pinecone =", file_id)
        namespace = file_id
        lines = read_file_lines(file, file_type)
        line_ids = [hashlib.sha256(line.encode()).hexdigest() for line in lines]

        # Fetch the file from Pinecone
        response = index.fetch(ids=line_ids, namespace=namespace)
        return len(response['vectors'].keys()) != 0
    
    except Exception as e:
        print(f"Error while checking {file_type} existence in Pinecone: {e}")
        return False

# Delete the file from Pinecone
def delete_file_from_pinecone(file, file_type):
    try:
        file_id = generate_id_from_file(file, file_type)
        print("namespace at delete_file_from_pinecone =", file_id)
        namespace = file_id
        lines = read_file_lines(file, file_type)
        line_ids = [hashlib.sha256(line.encode()).hexdigest() for line in lines]

        # Delete the file from Pinecone if ids matched
        response = index.delete(ids=line_ids, namespace=namespace)
        print(f"delete_{file_type}_from_pinecone response", response)
    except Exception as e:
        print(f"Error while deleting {file_type} from Pinecone: {e}")

# Process the file and add to Pinecone
def process_file(file, file_type):
    file_id = generate_id_from_file(file, file_type)
    namespace = file_id

    print(f"Processing {file_type} in namespace: {namespace}")

    if check_if_file_exists_in_pinecone(file, file_type):
        print(f"{file_type.upper()} already exists in Pinecone.")
        return

    lines = read_file_lines(file, file_type)
    to_upsert = []

    # Upsert each line in Pinecone
    for line in lines:
        line_id = hashlib.sha256(line.encode()).hexdigest()
        line_embedding = get_embedding(line)
        metadata = {"text": line}
        to_upsert.append({"id": line_id, "values": line_embedding, "metadata": metadata})

    if to_upsert:
        index.upsert(vectors=to_upsert, namespace=namespace)
        print("Ingesting DONE.")
    else:
        print("No vectors to upsert.")

# Query the Pinecone to get matching texts
def query_file(text_query, namespace, top_k=16):
    try:
        query_embedding = get_embedding(text_query)
        response = index.query(queries=[query_embedding], include_metadata=True, namespace=namespace, top_k=top_k)
        print("namespace at query_file =", namespace)
        matches = response['results'][0]['matches']
        file_texts = [match['metadata']['text'] for match in matches]
        return file_texts
    except Exception as e:
        print(f"Error while querying: {e}")
        return []

# Ensure the logs directory exists
os.makedirs('/app/data/logs', exist_ok=True)

# Engage in conversation using the GPT-3.5 model
def conversation_model(text_query, namespace):
    # Query Pinecone to get top matching docx texts
    file_texts = query_file(text_query, namespace)
    print("namespace at conversation_gpt_3_5 =", namespace)
    # Construct the Pinecone answer string
    pinecone_answer = ' '.join(file_texts)

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

    # Log the prompt and response
    with open('/app/data/logs/llm_interactions.log', 'a', encoding='utf-8') as log_file:
        log_file.write(f"Prompt: {text_query}\n")
        log_file.write(f"Response: {response_text}\n\n")

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
            delete_file_name = input("Please enter the file name (including extension) in the same directory to delete: ")
            
            if delete_file_name.endswith('.pdf'):
                file_type = 'pdf'
            elif delete_file_name.endswith('.docx'):
                file_type = 'docx'
            else:
                print("Unsupported file type. Only .pdf and .docx are allowed.")
                continue

            with open(delete_file_name, 'rb') as delete_file:
                delete_file_from_pinecone(delete_file, file_type)
                print(f"File {delete_file_name} has been deleted from Pinecone.")
            continue

        elif action.lower() == "query" or action.lower() == "change":
            file_name = input("Please enter the file name (including extension) in the same directory: ")

            if file_name.endswith('.pdf'):
                file_type = 'pdf'
            elif file_name.endswith('.docx'):
                file_type = 'docx'
            else:
                print("Unsupported file type. Only .pdf and .docx are allowed.")
                continue

            with open(file_name, 'rb') as file:
                # Check if the file has already been ingested
                if check_if_file_exists_in_pinecone(file, file_type):
                    print("File already ingested.")
                else:
                    print("File is not ingested. Ingesting now...")
                    process_file(file, file_type)
                    print("File is now ingested.")

                # Get the file's unique ID
                namespace = generate_id_from_file(file, file_type)

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
