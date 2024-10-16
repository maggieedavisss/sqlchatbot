import os
import openai
import pandas as pd
from sqlalchemy import create_engine, text

# Load environment variables (make sure you have these set)
openai_api_key = os.getenv('OPENAI_API_KEY')
azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
openai.api_key = openai_api_key

# Database setup (using SQLite in this example)
database_file_path = "./data/ms_etf_test.db"
cs = f'sqlite:///{database_file_path}'
db_engine = create_engine(cs)

# Function to execute SQL query on the database and return results
def execute_sql_query(sql_query):
    try:
        with db_engine.connect() as connection:
            result = connection.execute(text(sql_query))
            return result.fetchall()
    except Exception as e:
        return f"An error occurred while executing the query: {str(e)}"

# Function to generate SQL using OpenAI's GPT model
def generate_sql_query(question):
    try:
        # Define the system prompt and user prompt
        prompt = f"""
        You are an assistant that translates user questions into SQL queries. 
        The database contains two tables: 'etf_eom_perform' and 'etf_ref'. 
        'etf_ref' contains information about ETFs like ticker, active_status, and fund_standard_name. 
        'etf_eom_perform' contains end-of-month performance metrics like total_year_to_return_month_end. 
        The two tables are related by 'performance_id'. 
        Convert the following question into an SQL query:
        
        Question: {question}
        """

        # Call the OpenAI API (replace model with the appropriate Azure or OpenAI model)
        response = openai.Completion.create(
            engine="gpt-35-turbo",  # Change this to the correct model name if necessary
            prompt=prompt,
            max_tokens=150,
            temperature=0
        )

        # Extract the generated SQL query
        sql_query = response.choices[0].text.strip()
        return sql_query

    except Exception as e:
        return f"An error occurred while generating the SQL query: {str(e)}"

# Main SQL chatbot function
def sql_chatbot(question):
    try:
        # Generate the SQL query based on user input
        sql_query = generate_sql_query(question)

        # Execute the generated SQL query
        query_result = execute_sql_query(sql_query)

        return query_result

    except Exception as e:
        return f"An error occurred: {str(e)}"
