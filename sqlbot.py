import os
import pandas as pd
from sqlalchemy import create_engine, text
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType

# Load environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')
azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
database_file_path = "./data/ms_etf_test.db"

# Setup local DB engine and instance (using SQLite in this case)
cs = f'sqlite:///{database_file_path}'
db_engine = create_engine(cs)

# Function to execute SQL query on the database and return results
def execute_sql_query(sql_query):
    with db_engine.connect() as connection:
        result = connection.execute(text(sql_query))
        return result.fetchall()

# Setup Azure OpenAI model instance
model_deployment_name = "gpt-35-turbo"

llm = AzureChatOpenAI(
    azure_deployment=model_deployment_name,
    openai_api_key=openai_api_key,
    azure_endpoint=azure_endpoint,
    temperature=0, 
    max_tokens=500
)

# Custom prompt for generating SQL queries based on user input
prompt = ChatPromptTemplate.from_messages([
    ("system", """
        You are an intelligent AI assistant that helps generate SQL queries based on user questions. 
        Query the connected database, which has two tables: 'etf_eom_perform' and 'etf_ref'.
        The 'etf_ref' table contains ETF information, such as performance_id, ticker, and active_status.
        The 'etf_eom_perform' table contains end-of-month performance metrics for each ETF.
        Use 'performance_id' to join the tables when necessary to generate accurate results.
    """),
    ("user", "{question}")
])

# Define a function that integrates the LLM with SQL query execution
def sql_chatbot(question):
    try:
        # Generate SQL query from user input
        prompt_message = prompt.format_prompt(question=question)
        llm_response = llm(prompt_message).content
        
        # Execute the generated SQL query and return the results
        sql_result = execute_sql_query(llm_response)
        return sql_result
    
    except Exception as e:
        return f"An error occurred while processing the request: {str(e)}"
