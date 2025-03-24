import pinecone, openai, time
from PyPDF2 import PdfReader
import hashlib

openai.api_type = openai.api_type
openai.api_base = openai.api_base
openai.api_version = openai.api_version
openai.api_key = openai.api_key
vector_engine_name = vector_engine_name
turbo_engine_name = turbo_engine_name

# Initialize Pinecone
pinecone.init(api_key=api_key, environment="asia-southeast1-gcp-free")
index = pinecone.Index('connections')

def get_embedding(pdf_text):
    while True:
        try:
            response = openai.Embedding.create(engine=vector_engine_name, input=[pdf_text])
            embeds = response['data'][0]['embedding'] # Extracting the embedding list
            return embeds
        except Exception as e:
            print(f"Connection error: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)

def read_pdf_lines(file):
    try:
        pdf_reader = PdfReader(file)
        lines = []
        for page_num in range(len(pdf_reader.pages)):
            page_text = pdf_reader.pages[page_num].extract_text()
            lines.extend(page_text.splitlines())
        return lines
    except Exception as e:
        print(f"Error while reading PDF: {e}")
        return []

def generate_id_from_file(file):
    try:
        lines = read_pdf_lines(file)
        content = '\n'.join(lines)
        file_hash = hashlib.sha256(content.encode())
        return file_hash.hexdigest()
    except Exception as e:
        print(f"An error occurred while generating the ID for the file: {e}")
        return None

def check_if_pdf_exists_in_pinecone(file):
    try:
        pdf_id = generate_id_from_file(file)
        namespace = pdf_id
        lines = read_pdf_lines(file)
        line_ids = [hashlib.sha256(line.encode()).hexdigest() for line in lines]  # Vector IDs for every line

        # Fetch the vectors with the given line IDs from Pinecone
        response = index.fetch(ids=line_ids, namespace=namespace)
        
        # Return False if there are no keys, otherwise return True
        return len(response['vectors'].keys()) != 0
    
    except Exception as e:
        print(f"Error while checking PDF existence in Pinecone: {e}")
        return False

def delete_pdf_from_pinecone(file):
    try:
        pdf_id = generate_id_from_file(file) 
        namespace = pdf_id
        lines = read_pdf_lines(file)
        line_ids = [hashlib.sha256(line.encode()).hexdigest() for line in lines]  # Vector IDs for every line

        # Delete the vectors with the given line IDs from Pinecone
        response = index.delete(ids=line_ids, namespace=namespace)
        print("delete_pdf_from_pinecone response", response)

    except Exception as e:
        print(f"Error while deleting PDF from Pinecone: {e}")

def process_pdf(file):
    pdf_id = generate_id_from_file(file)
    namespace = pdf_id  # Set the namespace to be the generated ID from the file
    print(f"Processing PDF in namespace: {namespace}")

    if check_if_pdf_exists_in_pinecone(file):
        print("PDF already exists in Pinecone.")
        return

    lines = read_pdf_lines(file)
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

def query_pdf(text_query, namespace, top_k=20):
    try:
        query_embedding = get_embedding(text_query)
        response = index.query(queries=[query_embedding], include_metadata=True, namespace=namespace, top_k=top_k)
        
        matches = response['results'][0]['matches']
        pdf_texts = [match['metadata']['text'] for match in matches]  # Adjust this line according to the correct structure
        return pdf_texts
      
    except Exception as e:
        print(f"Error while querying PDF: {e}")
        return []

def conversation_model(text_query, namespace):
    # Query Pinecone to get top matching PDF texts
    pdf_texts = query_pdf(text_query, namespace)

    # Construct the Pinecone answer string
    pinecone_answer = ' '.join(pdf_texts)

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
                delete_pdf_from_pinecone(delete_file)
                print(f"File {delete_file_name} has been deleted from Pinecone.")
            continue
        elif action.lower() == "query" or action.lower() == "change":
            file_name = input("Please enter the file name (in the same directory): ")

            with open(file_name, 'rb') as file:
                # Check if the PDF file has already been ingested
                if check_if_pdf_exists_in_pinecone(file):
                    print("File already ingested.")
                else:
                    print("File is not ingested. Ingesting now...")
                    process_pdf(file)
                    print("File is now ingested.")

                # Get the PDF's unique ID
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





