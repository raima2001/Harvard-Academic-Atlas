from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

def commit_persona_usage(user_id, username, title, model_name, retrieval_mode, web_browsing_mode, code_interpreter_mode, private_usage, public_usage, input_tokens, output_tokens, timestamp):
    try:
        # Create a new Persona_Usage instance
        new_persona_usage = Persona_Usage(
            user_id=user_id,
            username=username,
            title=title,
            model_name=model_name,
            retrieval_mode=retrieval_mode,
            web_browsing_mode=web_browsing_mode,
            code_interpreter_mode=code_interpreter_mode,
            private_usage=private_usage,
            public_usage=public_usage,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            timestamp=timestamp
        )

        # Add the new instance to the session and commit
        db.session.add(new_persona_usage)
        db.session.commit()

        return True

    except Exception as e:
        # Handle the database error
        db.session.rollback()
        print(f"Database error: {e}")
        return False


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    openai_api_key = db.Column(db.String(500))  
    openai_api_key_salt = db.Column(db.String(500))
    serp_api_key = db.Column(db.String(500))  
    serp_api_key_salt = db.Column(db.String(500))
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    personas = db.relationship('Persona', backref='user', lazy=True)
    last_login = db.Column(db.String(200), nullable=False, default=datetime.utcnow)
    login_code = db.Column(db.Integer)
    needs_login_code = db.Column(db.Boolean, default=True, nullable=False)
    admin_keys_access = db.Column(db.String(255), nullable=False, default="Not Given")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'admin_keys_access': self.admin_keys_access,
            'username': self.username,
            'last_login': self.last_login,
            'login_code': self.login_code
        }

# Update the Persona model
class Persona(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    description=db.Column(db.Text, nullable=False)
    categories=db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(300))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_ids = db.Column(db.Text)  # Store as a JSON string
    web_browsing = db.Column(db.Boolean, default=False)
    code_interpreter = db.Column(db.Boolean, default=False)
    assistant_id = db.Column(db.String(120))  # Store the assistant ID
    public_url = db.Column(db.String(255), unique=True, nullable=True)
    is_public = db.Column(db.Boolean, default=False)
    is_public_without_key = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'title': self.title,
            'prompt': self.prompt,
            'description': self.description,
            'categories': self.categories,
            'image_url': self.image_url,
            'file_ids': self.file_ids,
            'web_browsing': self.web_browsing,
            'code_interpreter': self.code_interpreter,
            'assistant_id': self.assistant_id,
            'public_url': self.public_url,
            'is_public': self.is_public,
            'is_public_without_key': self.is_public_without_key
        }


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    model_name = db.Column(db.String(80), nullable=False)
    topic_name = db.Column(db.String(120), nullable=False)
    link = db.Column(db.String(500), nullable=False)
    input_tokens = db.Column(db.Integer)
    output_tokens = db.Column(db.Integer)
    timestamp = db.Column(db.String(200), nullable=False)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'topic_name': self.topic_name,
            'link': self.link,
            'model_name': self.model_name,
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'timestamp': self.timestamp
        }
    
    def user_to_dict(self):
        return {
            'topic_name': self.topic_name,
            'model_name': self.model_name,
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'timestamp': self.timestamp
        }


class Persona_Usage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    model_name = db.Column(db.String(80), nullable=False)
    retrieval_mode = db.Column(db.Boolean, default=False)
    web_browsing_mode = db.Column(db.Boolean, default=False)
    code_interpreter_mode = db.Column(db.Boolean, default=False)
    private_usage = db.Column(db.Boolean, default=False)
    public_usage = db.Column(db.Boolean, default=False)
    input_tokens = db.Column(db.Integer)
    output_tokens = db.Column(db.Integer)
    timestamp = db.Column(db.String(200), nullable=False)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'title': self.title,
            'model_name': self.model_name,
            'retrieval_mode': self.retrieval_mode,
            'web_browsing_mode': self.web_browsing_mode,
            'code_interpreter_mode': self.code_interpreter_mode,
            'private_usage': self.private_usage,
            'public_usage': self.public_usage,
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'timestamp': self.timestamp
        }
    
    def user_to_dict(self):
        return {
            'title': self.title,
            'model_name': self.model_name,
            'retrieval_mode': self.retrieval_mode,
            'web_browsing_mode': self.web_browsing_mode,
            'code_interpreter_mode': self.code_interpreter_mode,
            'private_usage': self.private_usage,
            'public_usage': self.public_usage,
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'timestamp': self.timestamp
        }

class KnowledgeFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    filename = db.Column(db.String(300), nullable=False)
    file_id = db.Column(db.String(300), nullable=True)  # New column for storing file ID
    file_size_in_gb = db.Column(db.Float)  # or db.String, depending on how you want to store the size
    timestamp = db.Column(db.String(200), nullable=False)

    def __init__(self, user_id, username, filename, file_id, file_size_in_gb, timestamp):
        self.user_id = user_id
        self.username = username
        self.filename = filename
        self.file_id = file_id
        self.file_size_in_gb = file_size_in_gb
        self.timestamp = timestamp

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'filename': self.filename,
            'file_id': self.file_id,
            'file_size_in_gb': self.file_size_in_gb,
            'timestamp': self.timestamp
        }
    
    def user_to_dict(self):
        return {
            'filename': self.filename,
            'file_id': self.file_id,
            'file_size_in_gb': self.file_size_in_gb,
            'timestamp': self.timestamp
        }
    

class GlobalVariable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email_domain = db.Column(db.String(255), nullable=False, unique=True, default="upskillr.ai")
    openai_api_key = db.Column(db.String(500))  
    openai_api_key_salt = db.Column(db.String(500))
    serp_api_key = db.Column(db.String(500))  
    serp_api_key_salt = db.Column(db.String(500))
    auto_admin_keys_access = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, email_domain="upskillr.ai"):
        self.email_domain = email_domain

    def to_dict(self):
        return {'email_domain': self.email_domain}

