from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/manage-file', methods=['POST'])
def manage_file():
    """
    This endpoint manages files: ingests, deletes, and queries them.
    """
    data = request.get_json()

    action = data.get('action', '').lower()
    file_name = data.get('file_name', '')
    text_query = data.get('text_query', '')

    if not action or not file_name:
        return jsonify({"error": "Action and file_name are mandatory parameters"}), 400

    if file_name.endswith('.pdf'):
        file_type = 'pdf'
    elif file_name.endswith('.docx'):
        file_type = 'docx'
    else:
        return jsonify({"error": "Unsupported file type. Only .pdf and .docx are allowed."}), 400

    response = {}

    if action == "delete":
        with open(file_name, 'rb') as delete_file:
            delete_file_from_pinecone(delete_file, file_type)
            response = {"message": f"File {file_name} has been deleted from Pinecone."}

    elif action == "query" or action == "change":
        with open(file_name, 'rb') as file:
            if not check_if_file_exists_in_pinecone(file, file_type):
                process_file(file, file_type)

            namespace = generate_id_from_file(file, file_type)
            response_text = conversation_gpt_3_5(text_query, namespace)
            response = {"response_text": response_text}

    else:
        return jsonify({"error": "Invalid action type. Use 'query', 'delete', or 'change'."}), 400

    return jsonify(response), 200

if __name__ == "__main__":
    app.run(debug=True)

"""
Demo JSON Input For deleting a file:

{
    "action": "delete",
    "file_name": "sample.pdf"
}

Demo JSON Input For querying a file::

{
    "action": "query",
    "file_name": "sample.docx",
    "text_query": "What is the capital of France?"
}

Expected JSON Output For deleting a file:

{
    "message": "File sample.pdf has been deleted from Pinecone."
}

Expected JSON Output For querying a file:

{
    "response_text": "The capital of France is Paris."
}

"""
