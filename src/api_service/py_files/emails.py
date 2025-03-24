import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml.shared import OxmlElement
import os, re

from Markdown2docx import Markdown2docx
import pypandoc, datetime, time, threading

# Email configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465
SMTP_USER = 'harvardacademicatlas@gmail.com'
SMTP_PASSWORD = 'akeb twwh xtmz savb'  # Replace with your actual password

def convert_and_delete_conversation_to_docx(heading, description, conversation, filename):
    """Converts conversation into markdown, then to docx, and deletes the markdown file."""
    def delayed_file_deletion(file_path: str, delay_in_seconds: int = 30): #22
        """Deletes the specified file after a delay."""
        print(f"Waiting for {delay_in_seconds} seconds before deleting {file_path}...")
        time.sleep(delay_in_seconds)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"File {file_path} deleted successfully.")
            else:
                print(f"File {file_path} does not exist.")
        except OSError as e:
            print(f"Error while deleting file {file_path}: {e}")

    print("Starting conversion and deletion process...")
    UPLOAD_FOLDER_CHAT_EMAILS = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'chat_emails')
    print(f"UPLOAD_FOLDER_CHAT_EMAILS set to: {UPLOAD_FOLDER_CHAT_EMAILS}")

    extracted_filename = os.path.basename(filename)
    print(f"Extracted filename: {extracted_filename}")

    filename_md = extracted_filename.replace('.docx', '.md')
    file_path_md = os.path.join(UPLOAD_FOLDER_CHAT_EMAILS, filename_md)
    print(f"Markdown file path set to: {file_path_md}")

    # Ensure the directory exists
    if not os.path.exists(os.path.dirname(file_path_md)):
        print(f"Creating directory for markdown file: {os.path.dirname(file_path_md)}")
        os.makedirs(os.path.dirname(file_path_md), exist_ok=True)

    # Write the Markdown file
    try:
        print(f"Writing markdown content to {file_path_md}...")
        with open(file_path_md, 'w', encoding='utf-8') as md_file:
            md_file.write(f"**Persona Name: {heading}**\n\n")
            md_file.write(f"Persona Description: {description}\n\n\n\n")
            for chat in conversation:
                role = chat['role'].title()
                content = chat['content']
                md_file.write(f"**{role}:** {content}\n\n")
            md_file.write("\n\n\n\n                              MasalaChai ❤\n")
        print("Markdown file created successfully.")
    except Exception as e:
        print(f"Error while creating Markdown file {file_path_md}: {e}")
        return None

    # Convert Markdown to DOCX
    try:
        print(f"Converting {file_path_md} to DOCX...")
        pypandoc.convert_file(file_path_md, 'docx', outputfile=filename)
        print("Conversion to DOCX completed successfully.")
    except Exception as e:
        print(f"Error while converting Markdown to DOCX for file {file_path_md}: {e}")
        return file_path_md  # Return MD path for manual deletion if needed

    # Schedule deletion of the Markdown file (set delay as needed)
    print(f"Scheduling deletion for {file_path_md}...")
    deletion_thread = threading.Thread(target=delayed_file_deletion, args=(file_path_md,))
    deletion_thread.start()

    # Return the path of the created Markdown file
    return file_path_md #82


def clean_text(text):
    # Remove markdown symbols and bold formatting
    text = re.sub(r'\*\*|\#|\#\#|\#\#\#', '', text) #87
    return text #88

# Function to create and save the Word document
def create_word_doc(heading, description, conversation, filename):
    try: #92
        doc = Document()

        # Heading with increased font size and center alignment
        heading_paragraph = doc.add_heading(heading, level=1)
        heading_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        for run in heading_paragraph.runs:
            run.font.size = Pt(16)

        # Add a line break after heading
        doc.add_paragraph()

        # Center aligned description
        description_paragraph = doc.add_paragraph(description)
        description_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        # Add a line break after description
        doc.add_paragraph()

        # Add conversation
        for chat in conversation:
            p = doc.add_paragraph()
            run = p.add_run(f"{chat['role'].title()}: ")
            run.bold = True
            clean_content = clean_text(chat['content'])
            p.add_run(clean_content)

        # Add closing statement with hyperlink
        doc.add_paragraph()
        closing_paragraph = doc.add_paragraph()
        closing_run = closing_paragraph.add_run("Powered by MasalaChai ❤\n")  # Line break after this text
        closing_run = closing_paragraph.add_run("harvardacademicatlas@gmail.com")
        closing_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        # Ensure the directory exists and save the document
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        doc.save(filename)
        return True
    except Exception as e:
        print(f"Error in create_word_doc: {e}")
        return False #132



# Function to send email with attachment
def send_email_with_attachment(to_email, subject, filename):
    try: #138
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = to_email
        msg['Subject'] = subject

        # Updated email body
        body = """
        <p>Please find the chat transcript attached. 📎</p>
        <p>Explore course recommendations and academic planning at <a href="https://harvardacademia/signup">Harvard Academia Atlas</a> 🚀</p>
        <p><strong>Need Help or Have Questions?</strong> 💭</p>
        <p>If you encounter any issues or have questions, feel free to reach out! 📬 Drop us an email at <a href="mailto:harvardacademicatlas@gmail.com">harvardacademicatlas@gmail.com</a>. We’re here to make your experience with Harvard Academia Atlas seamless and fulfilling and will get back to you within 24 hours. 🕒</p>
        <p>Warm Regards, 🌟<br>Aditya Saxena, Raima Islam, Kumar Tanmay 🌍<br>Harvard Academia Atlas Creators</p>
        """
        msg.attach(MIMEText(body, 'html'))

        # Attach the document
        with open(filename, "rb") as file:
            part = MIMEApplication(file.read(), Name=os.path.basename(filename))
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(filename)}"'
        msg.attach(part)

        # Send the email
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False #168

def send_welcome_email(to_email, login_code, password):

    # Email subject
    subject = 'Welcome to the Harvard Academia Atlas Powered by MasalaChai 🚀'

    # Define the email content as a multi-line string
    message = f'''
    🎉 Congratulations and welcome to the Harvard Academia Atlas! We are thrilled to have you onboard this AI-powered academic assistant, created to enhance your course planning experience.

    🔑 Your Harvard Academia Atlas account password: {password}

    🔑🔑 Your One-Time Login Code: {login_code}

    🔗 Login Link: https://harvardacademia/signup

    🚀 Here’s What Harvard Academia Atlas Offers:

    1. Personalized Course Recommendations: Receive course suggestions tailored to your academic background, interests, and career goals.

    2. Conflict-Free Scheduling: Simplify planning with conflict-free schedules, ensuring you can focus on your academics without the hassle.

    3. Course Relevance Insights: Understand why each recommended course supports your career aspirations.

    4. Efficient Course Exploration: Navigate through Harvard Law and Business School offerings with data from the official Harvard Course Catalog, including prerequisites, cross-registration options, and availability.

    5. Balanced Workload: Manage your academics with insights into course loads and scheduling to help you balance other commitments.

    💡 Need Help or Have Questions?

    If you encounter any issues or have questions, please reach out to us at harvardacademicatlas@gmail.com. We’re here to make your experience with Harvard Academia Atlas seamless and fulfilling. Our team will respond within 24 hours.

    Warm Regards,  
    Aditya Saxena, Raima Islam, Kumar Tanmay 
    Harvard Academia Atlas Creators
    '''

    # Create message
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the message body
    msg.attach(MIMEText(message, 'plain'))

    # Send the email
    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return "Email sent successfully!"
    except Exception as e: #222
        return f"Failed to send email: {e}" #223


# Function to send email with attachment
def send_audio_email_with_attachment(to_email, subject, filename):
    try: #228
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = to_email
        msg['Subject'] = subject

        # Updated email body
        body = """
        <p>Please find the chat transcript attached. 📎</p>
        <p>Explore course recommendations and academic planning at <a href="https://harvardacademia/signup">Harvard Academia Atlas</a> 🚀</p>
        <p><strong>Need Help or Have Questions?</strong> 💭</p>
        <p>If you encounter any issues or have questions, feel free to reach out! 📬 Drop us an email at <a href="mailto:harvardacademicatlas@gmail.com">harvardacademicatlas@gmail.com</a>. We’re here to make your experience with Harvard Academia Atlas seamless and fulfilling and will get back to you within 24 hours. 🕒</p>
        <p>Warm Regards, 🌟<br>Aditya Saxena, Raima Islam, Kumar Tanmay 🌍<br>Harvard Academia Atlas Creators</p>
        """
        msg.attach(MIMEText(body, 'html'))

        # Attach the document
        with open(filename, "rb") as file:
            part = MIMEApplication(file.read(), Name=os.path.basename(filename))
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(filename)}"'
        msg.attach(part)

        # Send the email
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False #258

def send_invitation_email(invitee_email, subject, chat_url, unique_link, username, run_name):
    # Define the email content as a multi-line string
    message = f''' #262
    Hello,

    You have been invited by {username} to participate in {run_name}!

    Here are your details:
    - Form Link: {unique_link}
    - Chat URL: {chat_url}

    Please click on the unique link to join and participate. We're excited to have you with us!

    Best regards,
    The Team
    '''

    # Create message
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = invitee_email
    msg['Subject'] = subject

    # Attach the message body
    msg.attach(MIMEText(message, 'plain'))

    # Send the email
    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return "Invitation email sent successfully to {}".format(invitee_email)
    except Exception as e:
        return f"Failed to send invitation email: {e}" #294
