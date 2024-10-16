from flask import Flask, request, render_template
from sqlbot import sql_chatbot, static_chatbot_qa
import os

app = Flask(__name__)

# Load environment variables (only for local dev, Azure will manage env vars separately)
from dotenv import load_dotenv
load_dotenv()

# HTML template
html_template = 'index.html'

@app.route('/')
def index():
    return render_template(html_template)

@app.route('/process_query', methods=['POST'])
def process_query():
    try:
        # Get the input text from the form
        sentence = request.form['sentence']
        llm_response = sql_chatbot(sentence)        

    except Exception as e:
        # Handle any errors and provide feedback       
        llm_response = f"An error occurred: {str(e)}"
    
    # Return the result to the template
    return render_template(html_template, result=llm_response)

if __name__ == '__main__':
    # Only for local development, Azure will use gunicorn for production
    app.run(debug=True)
