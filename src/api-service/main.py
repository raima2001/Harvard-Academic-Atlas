from flask import Flask, Response,render_template, request, jsonify, redirect, url_for, session, flash
from flask_cors import CORS

from py_files.model import db, User, Persona, Course, KnowledgeFile, Evaluation, News, commit_persona_usage, commit_alumni_usage, Alumni_Usage, Persona_Usage, GlobalVariable, Alumni, AlumniKnowledgeBase
from py_files.retrieval import delete_assistant_and_file, saveFileOpenAI, startBotCreation, delete_assistant, startThreadCreation, runAssistant, process_url, sanitize_filename, compress_audio, compressed_audio_to_text_file
from py_files.emails import create_news_article_word_doc_2, send_invitation_email, convert_and_delete_conversation_to_docx, send_news_email_with_attachment, updated_send_news_email_with_attachment, create_news_article_word_doc, send_welcome_email, create_word_doc, send_email_with_attachment, send_email_with_multiple_attachments, send_audio_email_with_attachment
from py_files.others import calculate_token_count, is_openai_key_valid, is_serp_key_valid, allowed_file, allowed_file_knowledge, encrypt_api_key, decrypt_api_key, is_password_valid, delayed_file_deletion, encrypt_and_encode_api_key, decrypt_and_decode_api_key, save_and_resize_image, delayed_file_deletion_for_evaluation
from openai import OpenAI

import json, os, threading, hashlib, base64, openai, re, logging, time, requests, ast, random, gspread
from werkzeug.utils import secure_filename

from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from googleapiclient.discovery import build
from google.oauth2 import service_account

from os.path import splitext
from time import sleep
 
from cryptography.fernet import Fernet
 

app = Flask(__name__)
scheduler = BackgroundScheduler()

# Configure CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://104.198.147.52:5000",
]

cors = CORS(app, resources={r"/*": {"origins": CORS_ALLOWED_ORIGINS}})

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'uY9s@K2$!MZ@a%^wRaA*j^V&(' 
db.init_app(app)

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_EXTENSIONS_KNOWLEDGE = {'docx', 'html', 'json', 'md', 'pdf', 'pptx', 'txt'}
UPLOAD_FOLDER_KNOWLEDGE = 'knowledge_base'
UPLOAD_FOLDER_CHAT_EMAILS = 'chat_emails'

JSON_FILE_PATH = 'genial-retina-409607-a21360ede8f7.json'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize OpenAI API key and model
MODEL = os.env("MODEL")


if not scheduler.running:
    scheduler.start()

with app.app_context():
   if not scheduler.running:
       scheduler.start()


@app.route('/')
def index():
    is_logged_in = 'user_id' in session
    username = ""

    if is_logged_in:
        user_id = session['user_id']
        try:
            user = db.session.query(User).get(user_id)
            username = user.username if user else ""
        except Exception as e:
            # Log the exception and handle it as needed
            pass

    return render_template('index.html', is_logged_in=is_logged_in, username=username)


@app.route('/persona_dashboard')
def persona_dashboard():

    user_id = session.get('user_id')
    if not user_id:
        return jsonify(success=False, message="User not authenticated"), 401
    
    if user_id:
        try:
            user_id = session['user_id']
            personas = Persona.query.filter_by(user_id=user_id).all()
        except Exception as e:
            # Log the exception and handle it as needed
            personas = []
    else:
        personas = []

    return render_template('persona_dashboard.html', personas=personas, is_logged_in=user_id)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form.get('confirmPassword')
        # Form validation checks
        if not username or not password or confirm_password is None:
            flash("All fields are required", "error")
            return redirect(url_for('signup'))

        if '@' not in username:
            flash("Username must contain '@'", "error")
            return redirect(url_for('signup'))
        
        # Fetch the authorized email domain from the GlobalVariable table
        global_var = GlobalVariable.query.first()
        user_domain = username.split('@')[-1]  # Extract the domain from the username

        # Check if the authorized email domain is set and validate accordingly
        if global_var and global_var.email_domain:
            #authorized_domain = global_var.email_domain
            #print("authorized_domain: ", authorized_domain)
            #if user_domain.lower() != authorized_domain.lower():
            #    return render_template('error.html', error_message=f"Email domain must be {authorized_domain}", return_url=url_for('signup'))
            
            # Assuming global_var and global_var.email_domain are already defined
            authorized_domains = [global_var.email_domain, "g.harvard.edu", "fas.harvard.edu"]

            print("Authorized domains: ", authorized_domains)

            # Convert user_domain and all authorized domains to lower case for case-insensitive comparison
            user_domain_lower = user_domain.lower()
            authorized_domains_lower = [domain.lower() for domain in authorized_domains]

            if user_domain_lower not in authorized_domains_lower:
                # Joining the authorized domains into a string to display in the error message
                authorized_domains_str = ", ".join(authorized_domains)
                return render_template('error.html', error_message=f"Email domain must be one of the following: {authorized_domains_str}", return_url=url_for('signup'))

        if not is_password_valid(password):
            print("Password does not meet the required standards", "error")
            return render_template('error.html', error_message="Password does not meet the required standards", return_url=url_for('signup'))

        if password != confirm_password:
            print("Passwords do not match", "error")
            return render_template('error.html', error_message=f"Passwords do not match", return_url=url_for('signup'))

        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            print("Username already exists", "error")
            return render_template('error.html', error_message="Username already exists", return_url=url_for('signup'))
        
        # Generate a unique 5-digit login code
        login_code = random.randint(10000, 99999)

        # Ensure the generated login code is unique
        while User.query.filter_by(login_code=login_code).first() is not None:
            login_code = random.randint(10000, 99999)

        try:
            user = User(username=username, login_code=login_code)
            user.set_password(password)

            if global_var.auto_admin_keys_access:
                user.openai_api_key = global_var.openai_api_key
                user.openai_api_key_salt = global_var.openai_api_key_salt
                user.serp_api_key = global_var.serp_api_key
                user.serp_api_key_salt = global_var.serp_api_key_salt
                user.admin_keys_access = "Given"

            db.session.add(user)
            db.session.commit()
            
            # Send welcome email
            send_welcome_email(username, login_code, password)

        except Exception as e:
            print(e)
            db.session.rollback()  # Rollback the session in case of error
            flash("An error occurred while creating your account", "error")
            return redirect(url_for('signup'))

        return redirect(url_for('signin'))
    
    return render_template('signup.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        login_code = request.form.get('login_code', type=int)

        # Check for required fields
        user = User.query.filter_by(username=username).first()
        if not username or not password or (user is None) or (login_code is None and user and user.needs_login_code):
            flash("All fields are required", "error")
            return render_template('error.html', error_message="Invalid Credentials - Login Code is required if it is your first login. Check your signup email.", return_url=url_for('signin'))

        if user and user.check_password(password):
            # If login_code is needed, check it
            if user.needs_login_code and user.login_code != login_code:
                flash("Invalid login code", "error")
                return render_template('error.html', error_message="Invalid Credentials", return_url=url_for('signin'))
            
            # Set the last_login field
            ist_timezone = pytz.timezone('EMEA/NewYork')
            ist_now = datetime.now(ist_timezone)
            user.last_login = ist_now.strftime("%Y-%m-%d %H:%M")

            # Set needs_login_code to False after successful login with login_code
            if user.needs_login_code:
                user.needs_login_code = False

            # Update the user in the database
            db.session.commit()

            session['user_id'] = user.id  # Store user_id in session
            return redirect(url_for('index'))
        else:
            flash("Invalid Credentials", "error")
            return render_template('error.html', error_message="Invalid Credentials", return_url=url_for('signin'))

    return render_template('signin.html')


@app.route('/signout')
def signout():
    session.clear()  # Clear the session
    flash("You have been successfully signed out.", "info")
    return redirect(url_for('index'))


@app.route('/add_persona', methods=['POST'])
def add_persona():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify(success=False, message="User not authenticated"), 401

    user = User.query.get(user_id)
    if not user or not user.openai_api_key:
        return jsonify(success=False, message="OpenAI API key not set"), 403
    
    decrypted_api_key = decrypt_and_decode_api_key(user.openai_api_key, user.openai_api_key_salt)

    title = request.form.get('title')
    prompt = request.form.get('prompt')
    image = request.files.get('image')
    description = request.form.get('description')
    categories = request.form.getlist('category[]')  # This will be a list

    if not title or not prompt or not description or not categories:
        return jsonify(success=False, message="Missing required fields"), 400

    # Initialize file_ids and assistant_id as None
    file_ids = None
    assistant_id = None
    categories = list(set(categories))
    categories_unique = json.dumps(categories)

    web_browsing = request.form.get('web_browsing') == 'true'
    code_interpreter = request.form.get('code_interpreter') == 'true'

    selected_files = request.form.getlist('selected_files')
    if selected_files:
        # Fetch file IDs from the database
        file_id_list = []
        for filename in selected_files:
            knowledge_file = KnowledgeFile.query.filter_by(user_id=user_id, filename=filename).first()
            if knowledge_file:
                file_id_list.append(knowledge_file.file_id)
        
        try:
            assistant_id = startBotCreation(file_id_list, decrypted_api_key, title, prompt, retrieval = True, web_browsing = web_browsing, code_interpreter = code_interpreter)
            print(assistant_id)
            if assistant_id is None:
                raise Exception("Failed to create assistant.")
            # Convert file ID list to JSON string for storage
            file_ids = json.dumps(file_id_list)
        except Exception as e:
            return jsonify(success=False, message=str(e)), 500
        
    elif web_browsing or code_interpreter:
        # Fetch file IDs from the database
        print(web_browsing, code_interpreter)
        file_id_list = []        
        try:
            assistant_id = startBotCreation(file_id_list, decrypted_api_key, title, prompt, retrieval = False, web_browsing = web_browsing, code_interpreter = code_interpreter)
            print(assistant_id)
            if assistant_id is None:
                raise Exception("Failed to create assistant.")
            # Convert file ID list to JSON string for storage
            file_ids = json.dumps(file_id_list)
        except Exception as e:
            return jsonify(success=False, message=str(e)), 500

    # Handling image upload
    image_path = "static/images/harvard_atlas_logo.png"  # Default image path

    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        timestamped_filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], timestamped_filename)
        image.save(image_path)

    public_url = f"{request.host_url}share/{hashlib.sha256(f'{user.username}{title}'.encode()).hexdigest()}/{title.replace(' ', '-')}"

    # Create and save the new persona
    try:
        new_persona = Persona(
            title=title,
            prompt=prompt,
            description=description,
            categories=categories_unique,
            image_url=image_path,
            user_id=user_id,
            username = user.username,
            file_ids=file_ids,
            web_browsing = web_browsing,
            code_interpreter = code_interpreter,
            assistant_id=assistant_id,
            public_url=public_url,
            is_public=False
        )
        db.session.add(new_persona)
        db.session.commit()
        return jsonify(success=True)
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message=str(e)), 500


@app.route('/get_personas', methods=['GET'])
def get_personas():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify(success=False, message="User not authenticated"), 401

    try:
        personas = Persona.query.filter_by(user_id=user_id).all()
        persona_list = [
            {"id": p.id, "title": p.title, "image": url_for('static', filename=p.image_url.replace('\\', '/').replace('static/', '', 1))}
            for p in personas
        ]
        return jsonify({"personas": persona_list})
    except Exception as e:
        # Log the exception here
        return jsonify(success=False, message= "Error occured: " + str(e)), 500
    

@app.route('/get_persona/<int:persona_id>', methods=['GET'])
def get_persona(persona_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify(success=False, message="User not authenticated"), 401

    try:
        persona = Persona.query.get(persona_id)
        if persona and persona.user_id == user_id:
            selected_file_ids = json.loads(persona.file_ids) if persona.file_ids else []
            selected_files = KnowledgeFile.query.filter(KnowledgeFile.file_id.in_(selected_file_ids)).all()
            selected_filenames = [file.filename for file in selected_files]

            return jsonify(
                success=True,
                title=persona.title,
                prompt=persona.prompt,
                image_url=persona.image_url,
                selected_filenames=selected_filenames,
                web_browsing=persona.web_browsing,
                code_interpreter=persona.code_interpreter,
                description = persona.description,
                categories = ast.literal_eval(persona.categories)
            )
        else:
            return jsonify(success=False, message="Persona not found or access denied"), 404
    except Exception as e:
        # Log the exception here
        return jsonify(success=False, message= "Error occured: " + str(e)), 500


@app.route('/edit_persona', methods=['POST'])
def edit_persona():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify(success=False, message="User not authenticated"), 401

    persona_id = request.form.get('id')
    persona = Persona.query.get(persona_id)
    if not persona or persona.user_id != user_id:
        return jsonify(success=False, message="Persona not found or access denied"), 404

    user = User.query.get(persona.user_id)
    if not user.openai_api_key:
        return jsonify(success=False, message="OpenAI API key not set"), 403

    decrypted_api_key = decrypt_and_decode_api_key(user.openai_api_key, user.openai_api_key_salt)

    old_prompt = persona.prompt
    new_prompt = request.form['new_prompt']
    # Update persona attributes
    persona.title = request.form['new_title']
    persona.description = request.form['new_description']
    persona.prompt = request.form['new_prompt']
    persona.categories = json.dumps(list(set(request.form.getlist('new_category[]'))))

    # Handle the image update
    image = request.files.get('new_image')
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}")
        image.save(image_path)
        persona.image_url = image_path

    # Web browsing and code interpreter settings
    latest_web_browsing = request.form.get('web_browsing') == 'true'
    latest_code_interpreter = request.form.get('code_interpreter') == 'true'

    # Check for changes in settings
    settings_changed = persona.web_browsing != latest_web_browsing or persona.code_interpreter != latest_code_interpreter or old_prompt != new_prompt
    persona.web_browsing = latest_web_browsing
    persona.code_interpreter = latest_code_interpreter

    # Retrieve files for retrieval toggle
    retrieval_toggle = request.form.get('retrieval_toggle') == 'on'
    file_ids = []
    if retrieval_toggle:
        selected_files = request.form.getlist('selected_files')
        file_ids = [KnowledgeFile.query.filter_by(user_id=persona.user_id, filename=f).first().file_id for f in selected_files]

    # Check if update is needed
    need_update = set(file_ids) != set(json.loads(persona.file_ids or '[]')) or settings_changed

    if need_update:
        if persona.assistant_id:
            delete_assistant(persona.assistant_id, decrypted_api_key)
        try:
            assistant_id = startBotCreation(file_ids, decrypted_api_key, persona.title, persona.prompt, retrieval_toggle, latest_web_browsing, latest_code_interpreter)
            persona.assistant_id = assistant_id
            persona.file_ids = json.dumps(file_ids) if retrieval_toggle else None
        except Exception as e:
            return jsonify(success=False, message=str(e)), 500
    elif not retrieval_toggle and persona.assistant_id:
        delete_assistant(persona.assistant_id, decrypted_api_key)
        persona.file_ids = None
        persona.assistant_id = None

    db.session.commit()
    return jsonify(success=True)


@app.route('/delete_persona', methods=['POST'])
def delete_persona():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify(success=False, message="User not authenticated"), 401

    persona_id = request.form.get('id')
    if not persona_id:
        return jsonify(success=False, message="No Persona ID provided"), 400

    persona = db.session.get(Persona, persona_id)
    if persona and persona.user_id == user_id:
        try:
            # If there are related resources, ensure to delete or handle them here
            db.session.delete(persona)
            db.session.commit()
            return jsonify(success=True)
        except Exception as e:
            # Log the error here
            db.session.rollback()
            return jsonify(success=False, message="An error occurred during deletion " + str(e)), 500
    else:
        return jsonify(success=False, message="Persona not found or access denied"), 404


@app.route('/chat/<persona_title>/<int:persona_id>')
def chat(persona_title, persona_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify(success=False, message="User not authenticated"), 401

    user = User.query.get(user_id)
    if not user or not user.openai_api_key:
        return jsonify(success=False, message="OpenAI API key not set"), 403

    try:
        persona = Persona.query.get(persona_id)
        if persona and persona.title == persona_title and persona.user_id == user_id:
            persona.image_url = url_for('static', filename=persona.image_url.replace('\\', '/').replace('static/', '', 1))
            return render_template('chat.html', persona=persona)
        else:
            return render_template('error.html', error_message="Persona not found or access denied", return_url=url_for('index')), 404
    except Exception as e:
        # Consider logging the error here
        return jsonify(error="An internal error occurred: " + str(e)), 500


@app.route('/api/chat', methods=['GET', 'POST'])
def api_chat():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify(success=False, message="User not authenticated"), 401

    user = User.query.get(user_id)
    if not user or not user.openai_api_key:
        return jsonify(error="OpenAI API key not set for user"), 403

    decrypted_api_key = decrypt_and_decode_api_key(user.openai_api_key, user.openai_api_key_salt)
    decrypted_serp_api_key = decrypt_and_decode_api_key(user.serp_api_key, user.serp_api_key_salt)

    if request.method == 'POST':
        persona_id = request.json.get('persona_id')
        user_input = request.json.get('user_input', None)

        ist_timezone = pytz.timezone('Asia/Kolkata')
        ist_now = datetime.now(ist_timezone)

        persona = db.session.get(Persona, persona_id)
        if not persona:
            return jsonify(error="Persona not found"), 404

        # Create the initial system input
        system_input = persona.prompt
        conversation_start = [{"role": "system", "content": system_input}]

        # Get the conversation history from the request
        conversation = request.json.get('conversation', [])

        # Prepend the initial system message only if the conversation history is empty
        if not conversation:
            conversation = conversation_start
        else:
            # Ensure the system's initial prompt is the first message
            conversation = conversation_start + conversation

        # Execute if assistant_id is present
        if persona.assistant_id:
            thread_id = startThreadCreation(conversation, decrypted_api_key)
            message_text, reference = runAssistant(thread_id, persona.assistant_id, decrypted_api_key, decrypted_serp_api_key)
            num_tokens_input, num_tokens_output = calculate_token_count(conversation, message_text)
            commit_persona_usage(persona.user_id, persona.username, persona.title, model_name = "gpt-4-1106-preview", retrieval_mode = bool(persona.assistant_id), web_browsing_mode = persona.web_browsing, code_interpreter_mode = persona.code_interpreter, private_usage = (not persona.is_public), public_usage = persona.is_public, input_tokens = num_tokens_input, output_tokens = num_tokens_output, timestamp = ist_now.strftime("%Y-%m-%d %H:%M"))

            if reference:
                if isinstance(reference, list):
                    message_text += "\n\nReferences:"
                    for ref in reference:
                        message_text += f"\n- {ref}"
                else:
                    # Check if reference starts with "file-"
                    if reference.startswith("file-"):
                        # Query the KnowledgeFile database
                        knowledge_file = KnowledgeFile.query.filter_by(user_id=user_id, file_id=reference).first()
                        if knowledge_file:
                            # Use the filename from the database
                            message_text += f"\n\n[Reference: {knowledge_file.filename}]"
                        else:
                            # Fallback to reference if filename not found
                            message_text += f"\n\n[Reference: {reference}]"
                    else:
                        message_text += f"\n\n[Reference: {reference}]"

            return jsonify(message=message_text)

        # Fallback to default chat completions if no assistant ID
        try:
            client = OpenAI(api_key=decrypted_api_key)
            stream = client.chat.completions.create(
                model=MODEL,  # Replace with your model
                messages=conversation,
                max_tokens=4000,
                stream=False
            )

            commit_persona_usage(persona.user_id, persona.username, persona.title, model_name = stream.model, retrieval_mode = bool(persona.assistant_id), web_browsing_mode = persona.web_browsing, code_interpreter_mode = persona.code_interpreter, private_usage = (not persona.is_public), public_usage = persona.is_public, input_tokens = stream.usage.prompt_tokens, output_tokens = stream.usage.completion_tokens, timestamp = ist_now.strftime("%Y-%m-%d %H:%M"))
            return jsonify(message=stream.choices[0].message.content)

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return jsonify(error=str(e)), 500


@app.route('/update_key', methods=['POST'])
def update_key():
    if 'user_id' not in session:
        return jsonify(success=False, message="User not authenticated"), 401

    user_id = session['user_id']
    user = db.session.query(User).get(user_id)
    if not user:
        return jsonify(success=False, message="User not found"), 404

    openai_api_key = request.form.get('openai_api_key')
    if openai_api_key:
        # Validate the openai_api_key
        if is_openai_key_valid(openai_api_key):
            try:
                encoded_api_key, encoded_salt = encrypt_and_encode_api_key(openai_api_key)
                user.openai_api_key = encoded_api_key
                user.openai_api_key_salt = encoded_salt
                db.session.commit()
                return jsonify(success=True, message="API key updated successfully")
            except Exception as e:
                db.session.rollback()
                # Log the exception here
                return jsonify(success=False, message="An error occurred while updating the API key: " + str(e)), 500
        else:
            return jsonify(success=False, message="Invalid OpenAI API key")

    return jsonify(success=False, message="No API key provided")


@app.route('/update_serp_key', methods=['POST'])
def update_serp_key():
    if 'user_id' not in session:
        return jsonify(success=False, message="User not authenticated"), 401

    user_id = session['user_id']
    user = db.session.query(User).get(user_id)
    if not user:
        return jsonify(success=False, message="User not found"), 404

    serp_api_key = request.form.get('serp_api_key')
    if serp_api_key:
        # Validate the openai_api_key
        if is_serp_key_valid(serp_api_key):
            try:
                encoded_api_key, encoded_salt = encrypt_and_encode_api_key(serp_api_key)
                user.serp_api_key = encoded_api_key
                user.serp_api_key_salt = encoded_salt
                db.session.commit()
                return jsonify(success=True, message="Google Custom Search API key updated successfully")
            except Exception as e:
                db.session.rollback()
                # Log the exception here
                return jsonify(success=False, message="An error occurred while updating the Google Custom Search API key: " + str(e)), 500
        else:
            return jsonify(success=False, message="Invalid Google Custom Search API key")

    return jsonify(success=False, message="No Google Custom Search API key provided")


@app.route('/delete_key', methods=['POST'])
def delete_key():
    if 'user_id' not in session:
        return jsonify(success=False, message="User not authenticated"), 401

    user_id = session['user_id']
    user = User.query.get(user_id)
    if not user:
        return jsonify(success=False, message="User not found"), 404

    try:
        user.openai_api_key = None  # Remove the key
        user.openai_api_key_salt = None
        db.session.commit()
        return jsonify(success=True, message="API key deleted successfully")
    except Exception as e:
        db.session.rollback()
        # Log the exception here
        return jsonify(success=False, message="An error occurred while deleting the API key: " + str(e)), 500


@app.route('/check_api_key', methods=['GET'])
def check_api_key():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify(success=False, message="User not authenticated"), 401

    try:
        user = db.session.query(User).get(user_id)
        return jsonify(success=True, has_key=bool(user and user.openai_api_key))
    except Exception as e:
        # Log the exception here
        return jsonify(success=False, message="An error occurred while checking the API key: " + str(e)), 500
    

@app.route('/check_both_api_key', methods=['GET'])
def check_api_both_key():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify(success=False, message="User not authenticated"), 401

    try:
        user = db.session.query(User).get(user_id)
        return jsonify(success=True, has_key=(bool(user and user.serp_api_key) and bool(user and user.openai_api_key)))
    except Exception as e:
        # Log the exception here
        return jsonify(success=False, message="An error occurred while checking Both API keys: " + str(e)), 500


@app.route('/check_api_validity', methods=['GET'])
def check_api_key_validity():
    try:
        openai_api_key = request.args.get('openai_api_key')  # Use args for GET request
        print(openai_api_key)
        if not openai_api_key:
            return jsonify(success=False, message="No API key provided")

        # Validate the openai_api_key
        if is_openai_key_valid(openai_api_key):
            return jsonify(success=True, message="API key is valid")
        else:
            return jsonify(success=False, message="Invalid OpenAI API key")

    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error during API key validation: {str(e)}")
        return jsonify(success=False, message="An error occurred during API key validation")
    

@app.route('/check_serp_api_validity', methods=['GET'])
def check_serp_api_key_validity():
    try:
        serp_api_key = request.args.get('serp_api_key')  # Use args for GET request
        print(serp_api_key)
        if not serp_api_key:
            return jsonify(success=False, message="No Google Custom Search API key provided")

        # Validate the openai_api_key
        if is_serp_key_valid(serp_api_key):
            return jsonify(success=True, message="Google Custom Search API key is valid")
        else:
            return jsonify(success=False, message="Invalid Google Custom Search API key")

    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error during API key validation: {str(e)}")
        return jsonify(success=False, message="An error occurred during Google Custom Search API key validation")


@app.route('/get_saved_key', methods=['GET'])
def get_saved_key():
    if 'user_id' not in session:
        return jsonify(success=False, message="User not authenticated"), 401

    user_id = session['user_id']
    user = User.query.get(user_id)
    if user:
        api_key_display = ""
        try:
            decrypted_api_key = decrypt_and_decode_api_key(user.openai_api_key, user.openai_api_key_salt)
        except:
            decrypted_api_key = False
        # Consider masking the key if exposing it is necessary

        if decrypted_api_key:
            api_key_display = decrypted_api_key

        return jsonify(success=True, openai_api_key=api_key_display)
    else:
        return jsonify(success=False, message="User not found"), 404


@app.route('/get_saved_serp_key', methods=['GET'])
def get_saved_serp_key():
    if 'user_id' not in session:
        return jsonify(success=False, message="User not authenticated"), 401

    user_id = session['user_id']
    user = User.query.get(user_id)
    if user:
        api_key_display = ""
        try:
            decrypted_api_key = decrypt_and_decode_api_key(user.serp_api_key, user.serp_api_key_salt)
        except:
            decrypted_api_key = False
        # Consider masking the key if exposing it is necessary

        if decrypted_api_key:
            api_key_display = decrypted_api_key

        return jsonify(success=True, serp_api_key=api_key_display)
    else:
        return jsonify(success=False, message="User not found"), 404


@app.route('/knowledge_base')
def knowledge_base():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to access the knowledge base.", "warning")
        return redirect(url_for('login'))  # Assuming 'login' is the endpoint for your login page

    # Include any additional context needed by the template
    return render_template('knowledge_base.html')


@app.route('/upload_link', methods=['POST'])
def upload_link():
    if 'user_id' not in session:
        return jsonify(success=False, message="User not authenticated"), 401

    user_id = session['user_id']
    user = db.session.query(User).get(user_id)
    if not user or not user.openai_api_key:
        return jsonify(success=False, message="OpenAI API key not set"), 403
    
    decrypted_api_key = decrypt_and_decode_api_key(user.openai_api_key, user.openai_api_key_salt)

    if 'link' not in request.form:
        return jsonify(success=False, message="No link received"), 400
    
    if 'linkName' not in request.form:
        return jsonify(success=False, message="No link name received"), 400

    link = request.form['link']
    file_name = request.form['linkName']

    success, file_content = process_url(link)
    if not success:
        return jsonify(success=False, message=file_content)
    
    try:
        file_name = sanitize_filename(file_name)
        # Save the extracted content as a .txt file
        timestamped_filename = f"{file_name}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.txt"
        user_folder = os.path.join(UPLOAD_FOLDER_KNOWLEDGE, f"{user_id}_{user.username}")
        os.makedirs(user_folder, exist_ok=True)

        file_path = os.path.join(user_folder, timestamped_filename)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(file_content)

        # Save file details to the database
        # (Assuming saveFileOpenAI and KnowledgeFile are defined similarly to upload_file)
        file_id = saveFileOpenAI(file_path, decrypted_api_key)
        if file_id is None:
            raise Exception("Failed to save file to OpenAI because file_id is None.")

        # Get the size of the file in bytes
        file_size_bytes = os.path.getsize(file_path)
        file_size_gb = file_size_bytes / (1024 * 1024 * 1024)
        ist_timezone = pytz.timezone('Asia/Kolkata')
        ist_now = datetime.now(ist_timezone)

        new_file = KnowledgeFile(user_id=user_id, username=user.username, filename=timestamped_filename.replace('.txt', ''), file_id=file_id, file_size=file_size_gb, timestamp =ist_now.strftime("%Y-%m-%d %H:%M"))
        db.session.add(new_file)
        db.session.commit()

        # Schedule the file for deletion after 10 minutes
        deletion_thread = threading.Thread(target=delayed_file_deletion, args=(file_path,))
        deletion_thread.start()
        return jsonify(success=True, file_name=timestamped_filename.replace('.txt', ''), file_id=file_id)

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error during link processing and saving: {e}")
        return jsonify(success=False, message="An error occurred during link processing"), 500


@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'user_id' not in session:
        return jsonify(success=False, message="User not authenticated"), 401

    user_id = session['user_id']
    user = db.session.query(User).get(user_id)
    if not user or not user.openai_api_key:
        return jsonify(success=False, message="OpenAI API key not set"), 403

    decrypted_api_key = decrypt_and_decode_api_key(user.openai_api_key, user.openai_api_key_salt)

    if 'file' not in request.files:
        return jsonify(success=False, message="No file part"), 400
    file = request.files['file']
    if file.filename == '' or not allowed_file_knowledge(file.filename):
        return jsonify(success=False, message="Invalid file type"), 400

    filename, file_extension = os.path.splitext(secure_filename(file.filename))
    timestamped_filename = f"{filename}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{file_extension}"
    user_folder = os.path.join(UPLOAD_FOLDER_KNOWLEDGE, f"{user_id}_{user.username}")
    os.makedirs(user_folder, exist_ok=True)
    file_path = os.path.join(user_folder, timestamped_filename)
    file.save(file_path)

    # Save the file details to the database
    try:
        if file_extension == ".mp3" or file_extension == ".mp4":
            compressed_file_path, compressed_size = compress_audio(file_path, user_folder)
            transcript_file_path = compressed_audio_to_text_file(compressed_file_path, user_folder, decrypted_api_key)
            file_id = saveFileOpenAI(transcript_file_path, decrypted_api_key)
            send_audio_email_with_attachment(user.username, "Audio File Transcript by Upskillr.ai", transcript_file_path)

            for path in [compressed_file_path, transcript_file_path]:
                deletion_thread = threading.Thread(target=delayed_file_deletion, args=(path,))
                deletion_thread.start()
        else:
            file_id = saveFileOpenAI(file_path, decrypted_api_key)

        if file_id is None:
            raise Exception("Failed to save file to OpenAI because file_id is None.")

        # Get the size of the file in bytes
        file_size_bytes = os.path.getsize(file_path)
        file_size_gb = round(file_size_bytes / (1024 * 1024 * 1024), 10)
        print(file_size_bytes, file_size_gb)
        ist_timezone = pytz.timezone('Asia/Kolkata')
        ist_now = datetime.now(ist_timezone)

        new_file = KnowledgeFile(user_id=user_id, username=user.username, filename=timestamped_filename, file_id=file_id, file_size_in_gb=file_size_gb, timestamp =ist_now.strftime("%Y-%m-%d %H:%M"))
        db.session.add(new_file)
        db.session.commit()

        # Schedule the file for deletion after 10 minutes
        deletion_thread = threading.Thread(target=delayed_file_deletion, args=(file_path,))
        deletion_thread.start()
        return jsonify(success=True, file_name=timestamped_filename, file_id=file_id)
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error during file upload and saving: {e}")

        # Attempt immediate file deletion in case of failure
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as delete_error:
            logging.error(f"Error during immediate file deletion: {delete_error}")

        return jsonify(success=False, message="An error occurred during file upload"), 500


@app.route('/delete_file', methods=['POST'])
def delete_file():
    if 'user_id' not in session:
        return jsonify(success=False, message="User not authenticated"), 401

    user_id = session['user_id']
    user = db.session.query(User).get(user_id)

    if not user:
        return jsonify(success=False, message="User not found"), 404
    
    decrypted_api_key = decrypt_and_decode_api_key(user.openai_api_key, user.openai_api_key_salt)

    file_name = request.form.get('file_name')
    knowledge_file = KnowledgeFile.query.filter_by(user_id=user_id, filename=file_name).first()

    if knowledge_file:
        # Check if the file is used in any persona
        personas_using_file = Persona.query.filter(Persona.user_id == user_id, Persona.file_ids.contains(knowledge_file.file_id)).all()
        if personas_using_file:
            return jsonify(success=False, message="Cannot delete file as it is in use by a persona"), 403

        # Attempt to delete the file from OpenAI's server if file_id is available
        if knowledge_file.file_id:
            try:
                client = OpenAI(api_key=decrypted_api_key)
                client.files.delete(knowledge_file.file_id)
            except Exception as e:
                return jsonify(success=False, message=f"Failed to delete file from OpenAI: {str(e)}"), 500

        # Remove the file record from the database
        db.session.delete(knowledge_file)
        db.session.commit()

        return jsonify(success=True)
    else:
        return jsonify(success=False, message="File not found in database"), 404


@app.route('/get_files', methods=['GET'])
def get_files():
    if 'user_id' not in session:
        return jsonify(success=False, message="User not authenticated"), 401
    user_id = session['user_id']
    try:
        user_files = KnowledgeFile.query.filter_by(user_id=user_id).all()
        file_names = [file.filename for file in user_files][::-1]
        return jsonify(file_names=file_names)
    except Exception as e:
        # Log error here
        return jsonify(success=False, message=str(e)), 500


@app.route('/get_persona_public_url/<int:persona_id>', methods=['GET'])
def get_persona_public_url(persona_id):
    if 'user_id' not in session:
        return jsonify(success=False, message="User not authenticated"), 401
    try:
        persona = Persona.query.get(persona_id)
        if persona:
            return jsonify(success=True, public_url=persona.public_url, is_public=persona.is_public, is_public_without_key=persona.is_public_without_key)
        else:
            return jsonify(success=False, message="Persona not found"), 404
    except Exception as e:
        # Log error here
        return jsonify(success=False, message=str(e)), 500


@app.route('/toggle_public_persona', methods=['POST'])
def toggle_public_persona():
    if 'user_id' not in session:
        return jsonify(success=False, message="User not authenticated"), 401

    user_id = session['user_id']
    user = User.query.get(user_id)
    if not user:
        return jsonify(success=False, message="User not found"), 404

    persona_id = request.form.get('persona_id')
    if not persona_id or not persona_id.isdigit():
        return jsonify(success=False, message="Invalid Persona ID"), 400

    make_public_input = request.form.get('make_public', '').lower()
    make_public = make_public_without_key = False
    if make_public_input in ['yes', 'true']:
        make_public = True
    elif make_public_input == 'yes_without_key':
        make_public_without_key = True
    elif make_public_input not in ['no', 'false']:
        return jsonify(success=False, message="Invalid public status value"), 400

    persona = Persona.query.filter_by(id=persona_id, user_id=user_id).first()
    if not persona:
        return jsonify(success=False, message="Persona not found or unauthorized"), 404

    try:
        persona.is_public = make_public
        persona.is_public_without_key = make_public_without_key
        db.session.commit()
        return jsonify(success=True, message="Persona public status updated", is_public=persona.is_public)
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message=str(e)), 500


@app.route('/share/<persona_hash>/<persona_name>')
def share_persona(persona_hash, persona_name):
    try:
        # Construct the full public URL from the request
        full_public_url = f"{request.host_url}share/{persona_hash}/{persona_name}"

        # Retrieve the public persona
        public_persona = Persona.query.filter_by(public_url=full_public_url).first()

        if public_persona and (public_persona.is_public or public_persona.is_public_without_key):
            image_url = url_for('static', filename=public_persona.image_url.replace('\\', '/').replace('static/', '', 1))

            # Retrieve the user who owns the persona and their OpenAI key
            user = User.query.get(public_persona.user_id)
            if user and user.openai_api_key:
                encryption_key = Fernet.generate_key()
                user_id_encrypt = encrypt_api_key(str(user.id), encryption_key)
                username_encrypt = encrypt_api_key(user.username, encryption_key)

                # Encode the encrypted data and key
                encoded_key = base64.urlsafe_b64encode(encryption_key).decode('utf-8')
                user_id_encrypt_encoded = base64.urlsafe_b64encode(user_id_encrypt).decode('utf-8')
                username_encrypt_encoded = base64.urlsafe_b64encode(username_encrypt).decode('utf-8')

                if public_persona.is_public:
                    return render_template('shared_chat.html', title=public_persona.title, persona_id=public_persona.id, admin_key_1=user_id_encrypt_encoded, admin_key_2=username_encrypt_encoded, salt=encoded_key, persona=public_persona, image=image_url)
                elif public_persona.is_public_without_key:
                    return render_template('shared_no_key_chat.html', title=public_persona.title, persona_id=public_persona.id, admin_key_1=user_id_encrypt_encoded, admin_key_2=username_encrypt_encoded, salt=encoded_key, persona=public_persona, image=image_url)
            else:
                return render_template('error.html', error_message="User's OpenAI key is missing", return_url=url_for('signup')), 500
        else:
            return render_template('error.html', error_message="Persona not found or is not public", return_url=url_for('signup')), 404

    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route('/api/shared_chat', methods=['POST'])
def shared_chat():
    try:
        data = request.json
        persona_id = data.get('persona_id')
        conversation = data.get('conversation')  # Define conversation here
        admin_user_id_encrypted_encoded = data.get('admin_key_1')
        admin_username_encrypted_encoded = data.get('admin_key_2')
        encrypted_key_encoded = data.get('salt')

        # Validate if all necessary data is present
        if not all([persona_id, conversation, admin_user_id_encrypted_encoded, admin_username_encrypted_encoded, encrypted_key_encoded]):
            return jsonify(error="Missing required data"), 400

        # Decrypting the keys
        try:
            encryption_key = base64.urlsafe_b64decode(encrypted_key_encoded.encode('utf-8'))
            admin_user_id_encrypted = base64.urlsafe_b64decode(admin_user_id_encrypted_encoded.encode('utf-8'))
            admin_username_encrypted = base64.urlsafe_b64decode(admin_username_encrypted_encoded.encode('utf-8'))
        except Exception as decryption_error:
            return jsonify(error=f"Decryption failed: {decryption_error}"), 500

        try:
            fernet = Fernet(encryption_key)
            admin_user_id = int(fernet.decrypt(admin_user_id_encrypted).decode())
            admin_username = fernet.decrypt(admin_username_encrypted).decode()
        except Exception as decryption_error:
            return jsonify(error=f"Invalid encrypted data: {decryption_error}"), 400

        # Check if the persona exists and is public
        persona = Persona.query.get(persona_id)
        if not persona or not persona.is_public:
            return jsonify(error="Persona not found or not public"), 404

        # Check if the user exists
        user = User.query.get(admin_user_id)
        if not user or user.username != admin_username:
            return jsonify(error="User not found or username does not match"), 404
        
        decrypted_api_key = decrypt_and_decode_api_key(user.openai_api_key, user.openai_api_key_salt)
        decrypted_serp_api_key = decrypt_and_decode_api_key(user.serp_api_key, user.serp_api_key_salt)

        try:
            ist_timezone = pytz.timezone('Asia/Kolkata')
            ist_now = datetime.now(ist_timezone)
            # Create the initial system input
            system_input = persona.prompt
            conversation_start = [{"role": "system", "content": system_input}]

            # Get the conversation history from the request
            conversation = request.json.get('conversation', [])

            # Prepend the initial system message only if the conversation history is empty
            if not conversation:
                conversation = conversation_start
            else:
                # Ensure the system's initial prompt is the first message
                conversation = conversation_start + conversation

            # Execute if assistant_id is present
            if persona.assistant_id:
                thread_id = startThreadCreation(conversation, decrypted_api_key)
                message_text, reference = runAssistant(thread_id, persona.assistant_id, decrypted_api_key, decrypted_serp_api_key)
                num_tokens_input, num_tokens_output = calculate_token_count(conversation, message_text)
                commit_persona_usage(persona.user_id, persona.username, persona.title, model_name = "gpt-4-1106-preview", retrieval_mode = bool(persona.assistant_id), web_browsing_mode = persona.web_browsing, code_interpreter_mode = persona.code_interpreter, private_usage = (not persona.is_public), public_usage = persona.is_public, input_tokens = num_tokens_input, output_tokens = num_tokens_output, timestamp = ist_now.strftime("%Y-%m-%d %H:%M"))

                if reference:
                    if isinstance(reference, list):
                        message_text += "\n\nReferences:"
                        for ref in reference:
                            message_text += f"\n- {ref}"
                    else:
                        # Check if reference starts with "file-"
                        if reference.startswith("file-"):
                            # Query the KnowledgeFile database
                            knowledge_file = KnowledgeFile.query.filter_by(user_id=admin_user_id, file_id=reference).first()
                            if knowledge_file:
                                # Use the filename from the database
                                message_text += f"\n\n[Reference: {knowledge_file.filename}]"
                            else:
                                # Fallback to reference if filename not found
                                message_text += f"\n\n[Reference: {reference}]"
                        else:
                            message_text += f"\n\n[Reference: {reference}]"

                return jsonify(message=message_text)

            # Fallback to default chat completions if no assistant ID
            client = OpenAI(api_key=decrypted_api_key)
            stream = client.chat.completions.create(
                model=MODEL,
                messages=conversation,
                max_tokens=4000,
                stream=False
            )
            commit_persona_usage(persona.user_id, persona.username, persona.title, model_name = stream.model, retrieval_mode = bool(persona.assistant_id), web_browsing_mode = persona.web_browsing, code_interpreter_mode = persona.code_interpreter, private_usage = (not persona.is_public), public_usage = persona.is_public, input_tokens = stream.usage.prompt_tokens, output_tokens = stream.usage.completion_tokens, timestamp = ist_now.strftime("%Y-%m-%d %H:%M"))
            return jsonify(message=stream.choices[0].message.content)

        except Exception as e:
            return jsonify(error=str(e)), 500
        
    except Exception as e:
        return jsonify(error=f"An unexpected error occurred: {str(e)}"), 500


@app.route('/api/shared_chat_without_key', methods=['POST'])
def shared_chat_without_key():
    try:
        data = request.json
        persona_id = data.get('persona_id')
        conversation = data.get('conversation')  # Define conversation here
        admin_user_id_encrypted_encoded = data.get('admin_key_1')
        admin_username_encrypted_encoded = data.get('admin_key_2')
        encrypted_key_encoded = data.get('salt')
        #apiKey = data.get('apiKey')
        #serpapiKey = data.get('serpapiKey')

        # Validate if all necessary data is present
        if not all([persona_id, conversation, admin_user_id_encrypted_encoded, admin_username_encrypted_encoded, encrypted_key_encoded]):
            return jsonify(error="Missing required data"), 400

        # Decrypting the keys
        try:
            encryption_key = base64.urlsafe_b64decode(encrypted_key_encoded.encode('utf-8'))
            admin_user_id_encrypted = base64.urlsafe_b64decode(admin_user_id_encrypted_encoded.encode('utf-8'))
            admin_username_encrypted = base64.urlsafe_b64decode(admin_username_encrypted_encoded.encode('utf-8'))
        except Exception as decryption_error:
            return jsonify(error=f"Decryption failed: {decryption_error}"), 500

        try:
            fernet = Fernet(encryption_key)
            admin_user_id = int(fernet.decrypt(admin_user_id_encrypted).decode())
            admin_username = fernet.decrypt(admin_username_encrypted).decode()
        except Exception as decryption_error:
            return jsonify(error=f"Invalid encrypted data: {decryption_error}"), 400

        # Check if the persona exists and is public
        persona = Persona.query.get(persona_id)
        if not persona or not persona.is_public_without_key:
            return jsonify(error="Persona not found or not public"), 404

        # Check if the user exists
        user = User.query.get(admin_user_id)
        if not user or user.username != admin_username:
            return jsonify(error="User not found or username does not match"), 404

        decrypted_api_key = decrypt_and_decode_api_key(user.openai_api_key, user.openai_api_key_salt) 
        decrypted_serp_api_key = decrypt_and_decode_api_key(user.serp_api_key, user.serp_api_key_salt)
        
        try:
            # Create the initial system input
            system_input = persona.prompt
            conversation_start = [{"role": "system", "content": system_input}]

            # Get the conversation history from the request
            conversation = request.json.get('conversation', [])

            # Prepend the initial system message only if the conversation history is empty
            if not conversation:
                conversation = conversation_start
            else:
                # Ensure the system's initial prompt is the first message
                conversation = conversation_start + conversation

            # Execute if assistant_id is present
            if persona.assistant_id:
                thread_id = startThreadCreation(conversation, decrypted_api_key)
                message_text, reference = runAssistant(thread_id, persona.assistant_id, decrypted_api_key, decrypted_serp_api_key)

                if reference:
                    if isinstance(reference, list):
                        message_text += "\n\nReferences:"
                        for ref in reference:
                            message_text += f"\n- {ref}"
                    else:
                        # Check if reference starts with "file-"
                        if reference.startswith("file-"):
                            # Query the KnowledgeFile database
                            knowledge_file = KnowledgeFile.query.filter_by(user_id=admin_user_id, file_id=reference).first()
                            if knowledge_file:
                                # Use the filename from the database
                                message_text += f"\n\n[Reference: {knowledge_file.filename}]"
                            else:
                                # Fallback to reference if filename not found
                                message_text += f"\n\n[Reference: {reference}]"
                        else:
                            message_text += f"\n\n[Reference: {reference}]"

                return jsonify(message=message_text)

            # Fallback to default chat completions if no assistant ID
            client = OpenAI(api_key=decrypted_api_key)
            stream = client.chat.completions.create(
                model=MODEL,
                messages=conversation,
                max_tokens=4000,
                stream=False
            )
            return jsonify(message=stream.choices[0].message.content)

        except Exception as e:
            return jsonify(error=str(e)), 500
        
    except Exception as e:
        return jsonify(error=f"An unexpected error occurred: {str(e)}"), 500


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if all required fields are received
        if not username or not password:
            return render_template('error.html', error_message="All fields are required", return_url=url_for('admin/login')), 400

        if username == 'Ba$AD9XTwa&UCgHdp)&Np7q' and password == 'Ba$AD9XTwa&UCgHdp)&Np7q':

            encryption_key = Fernet.generate_key()
            username_encrypt = encrypt_api_key(username, encryption_key)
            password_encrypt = encrypt_api_key(password, encryption_key)

            # Encode the encrypted data and key
            encoded_key = base64.urlsafe_b64encode(encryption_key).decode('utf-8')
            username_encoded = base64.urlsafe_b64encode(username_encrypt).decode('utf-8')
            password_encoded = base64.urlsafe_b64encode(password_encrypt).decode('utf-8')

            # Credentials are correct, render the admin panel
            return render_template('admin_panel.html', admin_key_1=username_encoded, admin_key_2=password_encoded, salt = encoded_key)
        
        else:
            # Incorrect credentials, redirect back to login with error
            flash('Invalid credentials for admin.', 'error')
            return redirect(url_for('admin_login'))

    # If GET request, render the login form
    return render_template('admin_login.html')


@app.route('/admin/api/users', methods=['POST'])
def admin_get_users():
    try:
        data = request.json
        admin_username_encrypted_encoded = data.get('admin_key_1')
        admin_password_encrypted_encoded = data.get('admin_key_2')
        encrypted_key_encoded = data.get('salt')

        # Validate if all necessary data is present
        if not all([admin_username_encrypted_encoded, admin_password_encrypted_encoded, encrypted_key_encoded]):
            return jsonify(error="Missing required data"), 400

        # Decrypting the keys
        try:
            encryption_key = base64.urlsafe_b64decode(encrypted_key_encoded.encode('utf-8'))
            admin_username_encrypted = base64.urlsafe_b64decode(admin_username_encrypted_encoded.encode('utf-8'))
            admin_password_encrypted = base64.urlsafe_b64decode(admin_password_encrypted_encoded.encode('utf-8'))

            fernet = Fernet(encryption_key)
            admin_username = fernet.decrypt(admin_username_encrypted).decode()
            admin_password = fernet.decrypt(admin_password_encrypted).decode()
        except Exception as e:
            return jsonify(error=f"Decryption error: {str(e)}"), 403

        # Validate Admin Credentials
        if admin_username != 'Ba$AD9XTwa&UCgHdp)&Np7q' or admin_password != 'Ba$AD9XTwa&UCgHdp)&Np7q':
            return jsonify(error="Unauthorized access"), 401

        # Retrieve Users from Database
        try:
            users = User.query.all()
            users_data = [user.to_dict() for user in users]  # Assuming User model has a to_dict method
            return jsonify(users_data)
        except Exception as e:
            return jsonify(error=f"Database error: {str(e)}"), 500

    except Exception as e:
        return jsonify(error=f"Server error: {str(e)}"), 500


@app.route('/admin/api/personas', methods=['POST'])
def admin_get_personas():
    try:
        data = request.json
        admin_username_encrypted_encoded = data.get('admin_key_1')
        admin_password_encrypted_encoded = data.get('admin_key_2')
        encrypted_key_encoded = data.get('salt')

        # Validate if all necessary data is present
        if not all([admin_username_encrypted_encoded, admin_password_encrypted_encoded, encrypted_key_encoded]):
            return jsonify(error="Missing required data"), 400

        # Decrypting the keys
        try:
            encryption_key = base64.urlsafe_b64decode(encrypted_key_encoded.encode('utf-8'))
            admin_username_encrypted = base64.urlsafe_b64decode(admin_username_encrypted_encoded.encode('utf-8'))
            admin_password_encrypted = base64.urlsafe_b64decode(admin_password_encrypted_encoded.encode('utf-8'))

            fernet = Fernet(encryption_key)
            admin_username = fernet.decrypt(admin_username_encrypted).decode()
            admin_password = fernet.decrypt(admin_password_encrypted).decode()
        except Exception as e:
            return jsonify(error=f"Decryption error: {str(e)}"), 403

        # Validate Admin Credentials
        if admin_username != 'Ba$AD9XTwa&UCgHdp)&Np7q' or admin_password != 'Ba$AD9XTwa&UCgHdp)&Np7q':
            return jsonify(error="Unauthorized access"), 401

        # Retrieve Users from Database
        try:
            personas = Persona.query.all()
            return jsonify([persona.to_dict() for persona in personas])
        except Exception as e:
            return jsonify(error=f"Database error: {str(e)}"), 500

    except Exception as e:
        return jsonify(error=f"Server error: {str(e)}"), 500


@app.route('/admin/api/courses', methods=['POST'])
def admin_get_courses():
    try:
        data = request.json
        admin_username_encrypted_encoded = data.get('admin_key_1')
        admin_password_encrypted_encoded = data.get('admin_key_2')
        encrypted_key_encoded = data.get('salt')

        # Validate if all necessary data is present
        if not all([admin_username_encrypted_encoded, admin_password_encrypted_encoded, encrypted_key_encoded]):
            return jsonify(error="Missing required data"), 400

        # Decrypting the keys
        try:
            encryption_key = base64.urlsafe_b64decode(encrypted_key_encoded.encode('utf-8'))
            admin_username_encrypted = base64.urlsafe_b64decode(admin_username_encrypted_encoded.encode('utf-8'))
            admin_password_encrypted = base64.urlsafe_b64decode(admin_password_encrypted_encoded.encode('utf-8'))

            fernet = Fernet(encryption_key)
            admin_username = fernet.decrypt(admin_username_encrypted).decode()
            admin_password = fernet.decrypt(admin_password_encrypted).decode()
        except Exception as e:
            return jsonify(error=f"Decryption error: {str(e)}"), 403

        # Validate Admin Credentials
        if admin_username != 'Ba$AD9XTwa&UCgHdp)&Np7q' or admin_password != 'Ba$AD9XTwa&UCgHdp)&Np7q':
            return jsonify(error="Unauthorized access"), 401

        # Retrieve Users from Database
        try:
            courses = Course.query.all()
            return jsonify([course.to_dict() for course in courses])
        except Exception as e:
            return jsonify(error=f"Database error: {str(e)}"), 500

    except Exception as e:
        return jsonify(error=f"Server error: {str(e)}"), 500


@app.route('/admin/api/files', methods=['POST'])
def admin_get_files():
    try:
        data = request.json
        admin_username_encrypted_encoded = data.get('admin_key_1')
        admin_password_encrypted_encoded = data.get('admin_key_2')
        encrypted_key_encoded = data.get('salt')

        # Validate if all necessary data is present
        if not all([admin_username_encrypted_encoded, admin_password_encrypted_encoded, encrypted_key_encoded]):
            return jsonify(error="Missing required data"), 400

        # Decrypting the keys
        try:
            encryption_key = base64.urlsafe_b64decode(encrypted_key_encoded.encode('utf-8'))
            admin_username_encrypted = base64.urlsafe_b64decode(admin_username_encrypted_encoded.encode('utf-8'))
            admin_password_encrypted = base64.urlsafe_b64decode(admin_password_encrypted_encoded.encode('utf-8'))

            fernet = Fernet(encryption_key)
            admin_username = fernet.decrypt(admin_username_encrypted).decode()
            admin_password = fernet.decrypt(admin_password_encrypted).decode()
        except Exception as e:
            return jsonify(error=f"Decryption error: {str(e)}"), 403

        # Validate Admin Credentials
        if admin_username != 'Ba$AD9XTwa&UCgHdp)&Np7q' or admin_password != 'Ba$AD9XTwa&UCgHdp)&Np7q':
            return jsonify(error="Unauthorized access"), 401

        # Retrieve Users from Database
        try:
            files = KnowledgeFile.query.all()
            return jsonify([file.to_dict() for file in files])
        except Exception as e:
            return jsonify(error=f"Database error: {str(e)}"), 500

    except Exception as e:
        return jsonify(error=f"Server error: {str(e)}"), 500


@app.route('/persona_marketplace')
def persona_marketplace():
    try:
        # Check if user is logged in
        user_id = session.get('user_id')
        if not user_id:
            flash("Please log in to access the Persona Marketplace.", "warning")
            return render_template('error.html', error_message="Please log in to access the Persona Marketplace.", return_url=url_for('signin')), 404

        # Fetch all personas where is_public_without_key is True
        personas = Persona.query.filter_by(is_public_without_key=True).all()

        # Convert personas to a list of dictionaries
        personas_data = [{
            'id': persona.id,
            'username': persona.username,
            'title': persona.title,
            'description': persona.description,
            'categories': ast.literal_eval(persona.categories),
            'image_url': persona.image_url,
            'public_url': persona.public_url
        } for persona in personas]

        # Add the list of categories to pass to the template
        categories = [
            "Software Development",
            "Business",
            "Finance and Accounting",
            "Office Productivity",
            "Personal Development",
            "Design",
            "Marketing",
            "Lifestyle",
            "Photography and Video",
            "Health and Fitness",
            "Music",
            "Teaching and Academics",
            "Others"
        ]

        return render_template('persona_marketplace.html', personas=personas_data, categories=categories)
    
    except Exception as e:
        print("Error: ", e)  # Log the actual error
        return render_template('error.html', error_message=str(e), return_url=url_for('index')), 500


@app.route('/api/email_chat', methods=['POST'])
def email_chat():
    if 'user_id' not in session:
        return jsonify(success=False, message="User not authenticated"), 401

    user_id = session['user_id']
    user = User.query.get(user_id)
    if not user:
        return jsonify(success=False, message="User not found"), 404

    email_id = user.username
    heading = request.json.get('personaName', '')
    description = request.json.get('personaDescription', '')
    conversation = request.json.get('conversation', [])

    if not conversation:
        return jsonify(success=False, message="No conversation data provided"), 400

    try:
        # Generate a unique filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"chat_{heading}_{email_id}_{timestamp}.docx"
        file_path = os.path.join(UPLOAD_FOLDER_CHAT_EMAILS, filename)

        # Create the Word document and save it
        convert_and_delete_conversation_to_docx(heading, description, conversation, file_path)

        # Send the email with the Word document attached
        send_email_with_attachment(email_id, 'Your Chat Transcript By Academia Atlas', file_path)

        # Schedule the file for deletion after 30 seconds
        deletion_thread = threading.Thread(target=delayed_file_deletion, args=(file_path,))
        deletion_thread.start()

        return jsonify(success=True, message="Email sent successfully")
    except Exception as e:
        try:
            deletion_thread = threading.Thread(target=delayed_file_deletion, args=(file_path,))
            deletion_thread.start()
        except:
            pass
        # Log the error here
        print(f"Error in email_chat: {e}")
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500
    

@app.route('/api/email_chat_with_email', methods=['POST'])
def email_chat_with_email():

    email_id = request.json.get('userEmail')

    if not email_id:
        jsonify(success=False, message="No email_id provided or invalid email id")

    heading = request.json.get('personaName', '')
    description = request.json.get('personaDescription', '')
    conversation = request.json.get('conversation', [])

    if not conversation:
        return jsonify(success=False, message="No conversation data provided"), 400

    try:
        # Generate a unique filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"chat_{heading}_{email_id}_{timestamp}.docx"
        file_path = os.path.join(UPLOAD_FOLDER_CHAT_EMAILS, filename)

        # Create the Word document and save it
        convert_and_delete_conversation_to_docx(heading, description, conversation, file_path)

        # Send the email with the Word document attached
        send_email_with_attachment(email_id, 'Your Chat Transcript By Academia Atlas', file_path)

        # Schedule the file for deletion after 30 seconds
        deletion_thread = threading.Thread(target=delayed_file_deletion, args=(file_path,))
        deletion_thread.start()

        return jsonify(success=True, message="Email sent successfully")
    except Exception as e:
        try:
            deletion_thread = threading.Thread(target=delayed_file_deletion, args=(file_path,))
            deletion_thread.start()
        except:
            pass
        # Log the error here
        print(f"Error in email_chat: {e}")
        return jsonify(success=False, message=f"An error occurred: {str(e)}"), 500


@app.route('/usage_history', methods=['GET', 'POST'])
def usage_history():

    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to access the Usage History.", "warning")
        return redirect(url_for('login'))  # Assuming 'login' is the endpoint for your login page

    return render_template('usage_history.html')


@app.route('/usage_history/api/', methods=['POST'])
def usage_history_api():

    user_id = session.get('user_id')
    if not user_id:
        return jsonify(success=False, message="User not authenticated"), 401
     
    # Query each model for user-specific data
    try:
        courses = Course.query.filter_by(user_id=user_id).all()
        persona_usages = Persona_Usage.query.filter_by(user_id=user_id).all()
        knowledge_files = KnowledgeFile.query.filter_by(user_id=user_id).all()
        evaluations = Evaluation.query.filter_by(user_id=user_id).all()
        news_items = News.query.filter_by(user_id=user_id).all()
        alumni_usages = Alumni_Usage.query.filter_by(user_id=user_id).all()

        # Convert the data to dictionaries
        courses_data = [course.user_to_dict() for course in courses]
        persona_usages_data = [usage.user_to_dict() for usage in persona_usages]
        knowledge_files_data = [file.user_to_dict() for file in knowledge_files]
        evaluations_data = [evaluation.user_to_dict() for evaluation in evaluations]
        news_items_data = [news.user_to_dict() for news in news_items]
        alumni_usages_data = [alumni.user_to_dict() for alumni in alumni_usages]
        # Combine all data into a single response
        response = {
            'courses': courses_data,
            'persona_usages': persona_usages_data,
            'knowledge_files': knowledge_files_data,
            'evaluations': evaluations_data,
            'news_items': news_items_data,
            'alumni_usage_data': alumni_usages_data
        }
        return jsonify(response)

    except Exception as e:
        return jsonify(error=f"Query error: {str(e)}"), 500


@app.route('/admin_access/api/', methods=['POST'])
def admin_access_api():
    try:
        data = request.json
        admin_username_encrypted_encoded = data.get('admin_key_1')
        admin_password_encrypted_encoded = data.get('admin_key_2')
        encrypted_key_encoded = data.get('salt')

        # Validate if all necessary data is present
        if not all([admin_username_encrypted_encoded, admin_password_encrypted_encoded, encrypted_key_encoded]):
            return jsonify(error="Missing required data"), 400

        # Decrypting the keys
        try:
            encryption_key = base64.urlsafe_b64decode(encrypted_key_encoded.encode('utf-8'))
            admin_username_encrypted = base64.urlsafe_b64decode(admin_username_encrypted_encoded.encode('utf-8'))
            admin_password_encrypted = base64.urlsafe_b64decode(admin_password_encrypted_encoded.encode('utf-8'))

            fernet = Fernet(encryption_key)
            admin_username = fernet.decrypt(admin_username_encrypted).decode()
            admin_password = fernet.decrypt(admin_password_encrypted).decode()
        except Exception as e:
            return jsonify(error=f"Decryption error: {str(e)}"), 403

        # Validate Admin Credentials
        if admin_username != 'Ba$AD9XTwa&UCgHdp)&Np7q' or admin_password != 'Ba$AD9XTwa&UCgHdp)&Np7q':
            return jsonify(error="Unauthorized access"), 401

        # Query all models and convert data to dictionaries
        try:
            users = User.query.all()
            personas = Persona.query.all()
            courses = Course.query.all()
            persona_usages = Persona_Usage.query.all()
            knowledge_files = KnowledgeFile.query.all()
            evaluations = Evaluation.query.all()
            news_items = News.query.all()
            alumni_usages = Alumni_Usage.query.all()
            # Function to categorize model names
            def categorize_model(model_name):
                if model_name.startswith('gpt-4'):
                    return 'gpt-4'
                elif model_name.startswith('gpt-3.5-turbo'):
                    return 'gpt-3.5-turbo'
                else:
                    return 'other'
                
            # Aggregate token counts for each user
            token_counts = {}
            for model_list in [courses, alumni_usages, persona_usages, evaluations, news_items]:
                for model in model_list:
                    category = categorize_model(model.model_name if hasattr(model, 'model_name') else model.selected_model)
                    if category != 'other':
                        key = (model.user_id, category)
                        if key not in token_counts:
                            token_counts[key] = {'input_tokens': 0, 'output_tokens': 0}
                        token_counts[key]['input_tokens'] += model.input_tokens or 0
                        token_counts[key]['output_tokens'] += model.output_tokens or 0

            # Append token data to user data
            users_data = []
            for user in users:
                user_dict = user.to_dict()
                for category in ['gpt-4', 'gpt-3.5-turbo']:
                    key = (user.id, category)
                    if key in token_counts:
                        user_dict[f'{category}_input_tokens'] = token_counts[key]['input_tokens']
                        user_dict[f'{category}_output_tokens'] = token_counts[key]['output_tokens']
                    else:
                        user_dict[f'{category}_input_tokens'] = 0
                        user_dict[f'{category}_output_tokens'] = 0
                users_data.append(user_dict)

            personas_data = [persona.to_dict() for persona in personas]
            courses_data = [course.to_dict() for course in courses]
            persona_usages_data = [usage.to_dict() for usage in persona_usages]
            knowledge_files_data = [file.to_dict() for file in knowledge_files]
            evaluations_data = [evaluation.to_dict() for evaluation in evaluations]
            news_items_data = [news.to_dict() for news in news_items]
            alumni_usage_data = [alumni.to_dict() for alumni in alumni_usages]
            # Combine all data into a single response
            response = {
                'users': users_data,
                'personas': personas_data,
                'courses': courses_data,
                'persona_usages': persona_usages_data,
                'knowledge_files': knowledge_files_data,
                'evaluations': evaluations_data,
                'news_items': news_items_data,
                'alumni_usage_data': alumni_usage_data
            }
            return jsonify(response)

        except Exception as e:
            return jsonify(error=f"Query error: {str(e)}"), 500

    except Exception as e:
        return jsonify(error=f"Server error: {str(e)}"), 500
    

@app.route('/admin/global_variable_email_domain', methods=['GET', 'POST'])
def update_global_variable_email_domain():
    if request.method == 'GET':
        # Fetch the existing global variable
        global_var = GlobalVariable.query.first()
        if global_var:
            return jsonify(email_domain=global_var.email_domain)
        else:
            # If not found, initialize with default value and save
            global_var = GlobalVariable(email_domain="upskillr.ai")
            db.session.add(global_var)
            db.session.commit()
            return jsonify(email_domain="upskillr.ai")
        
    elif request.method == 'POST':
        try:
            data = request.json
            email_domain = data.get('email_domain')
            admin_username_encrypted_encoded = data.get('admin_key_1')
            admin_password_encrypted_encoded = data.get('admin_key_2')
            encrypted_key_encoded = data.get('salt')

            if not all([admin_username_encrypted_encoded, admin_password_encrypted_encoded, encrypted_key_encoded, email_domain]):
                return jsonify(error="Missing required data"), 400
            
            # Decrypting the keys
            try:
                encryption_key = base64.urlsafe_b64decode(encrypted_key_encoded.encode('utf-8'))
                admin_username_encrypted = base64.urlsafe_b64decode(admin_username_encrypted_encoded.encode('utf-8'))
                admin_password_encrypted = base64.urlsafe_b64decode(admin_password_encrypted_encoded.encode('utf-8'))

                fernet = Fernet(encryption_key)
                admin_username = fernet.decrypt(admin_username_encrypted).decode()
                admin_password = fernet.decrypt(admin_password_encrypted).decode()
            except Exception as e:
                return jsonify(error=f"Decryption error: {str(e)}"), 403

            # Validate Admin Credentials
            if admin_username != 'Ba$AD9XTwa&UCgHdp)&Np7q' or admin_password != 'Ba$AD9XTwa&UCgHdp)&Np7q':
                return jsonify(error="Unauthorized access"), 401

            # Assuming there's always one global variable entry, get the first one
            global_var = GlobalVariable.query.first()
            if not global_var:
                # Create new entry if it doesn't exist
                global_var = GlobalVariable(email_domain=email_domain.lower())
                db.session.add(global_var)
            else:
                # Update existing entry
                global_var.email_domain = email_domain.lower()

            db.session.commit()
            return jsonify(success=True, message="Updated")

        except Exception as e:
            db.session.rollback()
            return jsonify(success=False, message=f"Error: {str(e)}"), 500


@app.route('/admin/global_variable_api_keys', methods=['GET', 'POST'])
def update_global_variable_api_keys():
        
    try:
        if request.method == 'GET':
            global_var = GlobalVariable.query.first()
            if global_var:
                decrypted_api_key = decrypt_and_decode_api_key(global_var.openai_api_key, global_var.openai_api_key_salt)
                decrypted_serp_api_key = decrypt_and_decode_api_key(global_var.serp_api_key, global_var.serp_api_key_salt)
                return jsonify(success=True, openai_api_key=decrypted_api_key, serp_api_key=decrypted_serp_api_key)
            return jsonify(success=False, message="Global variable not found")

        elif request.method == 'POST':
            data = request.get_json()
            required_fields = ['open_ai_key', 'google_search_api_key']
            if not all(field in data for field in required_fields):
                return jsonify(success=False, message="Missing required data")

            encrypted_key_encoded, admin_username_encrypted_encoded, admin_password_encrypted_encoded = \
                data['salt'], data['admin_key_1'], data['admin_key_2']

            encryption_key = base64.urlsafe_b64decode(encrypted_key_encoded.encode('utf-8'))
            admin_username_encrypted = base64.urlsafe_b64decode(admin_username_encrypted_encoded.encode('utf-8'))
            admin_password_encrypted = base64.urlsafe_b64decode(admin_password_encrypted_encoded.encode('utf-8'))

            fernet = Fernet(encryption_key)
            admin_username = fernet.decrypt(admin_username_encrypted).decode()
            admin_password = fernet.decrypt(admin_password_encrypted).decode()

            if admin_username != 'Ba$AD9XTwa&UCgHdp)&Np7q' or admin_password != 'Ba$AD9XTwa&UCgHdp)&Np7q':
                return jsonify(success=False, message="Unauthorized access")

            global_var = GlobalVariable.query.first_or_404(description='Global variable not found')

            serp_key_valid = is_serp_key_valid(data['google_search_api_key'])
            openai_key_valid = is_openai_key_valid(data['open_ai_key'])

            if not serp_key_valid and not openai_key_valid:
                return jsonify(success=False, message="Both OpenAI key and Google API key are invalid"), 400
            if not openai_key_valid:
                return jsonify(success=False, message="OpenAI key is invalid"), 400
            if not serp_key_valid:
                return jsonify(success=False, message="Google API key is invalid"), 400

            if serp_key_valid:
                encoded_api_key, encoded_salt = encrypt_and_encode_api_key(data['google_search_api_key'])
                global_var.serp_api_key = encoded_api_key
                global_var.serp_api_key_salt = encoded_salt

            if openai_key_valid:
                encoded_api_key, encoded_salt = encrypt_and_encode_api_key(data['open_ai_key'])
                global_var.openai_api_key = encoded_api_key
                global_var.openai_api_key_salt = encoded_salt

            db.session.commit()
            return jsonify(success=True, message="Updated successfully")

    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message=f"Server error: {str(e)}"), 500


@app.route('/admin/global_variable_auto_access_admin_keys', methods=['POST'])
def update_auto_access_admin_keys():
    data = request.get_json()
    auto_access = data.get('auto_admin_keys_access', False)
    
    try:
        global_var = GlobalVariable.query.first() 
        if global_var:
            # Check if both API keys are set
            if global_var.openai_api_key and global_var.serp_api_key:
                global_var.auto_admin_keys_access = auto_access
                db.session.commit()
                return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'message': 'Admin keys need to be filled first'})
        else:
            return jsonify({'success': False, 'message': 'Global variable record not found'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/admin/get_auto_access_admin_keys_status', methods=['GET'])
def get_auto_access_admin_keys_status():
    try:
        global_var = GlobalVariable.query.first()
        if global_var:
            return jsonify(success=True, auto_admin_keys_access=global_var.auto_admin_keys_access)
        else:
            return jsonify(success=False, message="Global variable record not found")
    except Exception as e:
        return jsonify(success=False, message=str(e))


@app.route('/admin/global_variable_logo_image', methods=['POST'])
def upload_logo():
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'})

    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'})

    if file:
        filename = 'admin_logo.png'
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        if os.path.exists(file_path):
            os.remove(file_path)

        file.save(file_path)

        return jsonify({'success': True, 'filename': filename})

    return jsonify({'success': False, 'message': 'Invalid file'})


@app.route('/admin/send-user-data', methods=['POST'])
def admin_handle_user_data():
    try:
        # Extract user_id from the request, ensuring it's provided
        user_id = request.json.get('user_id')
        if not user_id:
            return jsonify(success=False, message='User ID is required')

        # Retrieve the global variables
        global_vars = GlobalVariable.query.first()
        if not global_vars:
            return jsonify(success=False, message='Global variables not found')

        # Retrieve the user by ID
        user = User.query.get(user_id)
        if not user:
            return jsonify(success=False, message='User not found')
        
        if user.admin_keys_access == "Not Given":
            # Update the user's keys
            user.openai_api_key = global_vars.openai_api_key
            user.openai_api_key_salt = global_vars.openai_api_key_salt
            user.serp_api_key = global_vars.serp_api_key
            user.serp_api_key_salt = global_vars.serp_api_key_salt
            user.admin_keys_access = "Given"

        elif user.admin_keys_access == "Given":
            user.openai_api_key = None
            user.openai_api_key_salt = None
            user.serp_api_key = None
            user.serp_api_key_salt = None
            user.admin_keys_access = "Not Given"

        # Commit changes to the database
        db.session.commit()
        return jsonify(success=True, message='User data updated successfully', user_id=user_id)

    except Exception as e:
        db.session.rollback()
        return jsonify(success= False, message='An unexpected error occurred' + str(e)), 500
    

if __name__ == '__main__':
    try:
        with app.app_context():
            db.create_all()
        app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)
    finally:
        if scheduler.running:
            scheduler.shutdown()
