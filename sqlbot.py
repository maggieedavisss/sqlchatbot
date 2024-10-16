import os
import pandas as pd
from sqlalchemy import create_engine
from langchain_openai import AzureChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents.agent_types import AgentType

# Load environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')
azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
database_file_path = "./data/ms_etf_test.db"

# Setup local DB engine and instance (if using SQLite)
cs = f'sqlite:///{database_file_path}'
db_engine = create_engine(cs)
db_instance = SQLDatabase(db_engine)

# Setup Azure OpenAI model instance
model_deployment_name = "gpt-35-turbo"

llm = AzureChatOpenAI(
    azure_deployment=model_deployment_name,
    openai_api_key=openai_api_key,
    azure_endpoint=azure_endpoint,
    temperature=0, 
    max_tokens=500
)

sql_toolkit = SQLDatabaseToolkit(db=db_instance, llm=llm)

prompt = ChatPromptTemplate.from_messages([
    ("system", """
        You are an intelligent AI assistant who converts user questions into SQL queries.
        Query the connected database, which has two tables: 'etf_eom_perform' and 'etf_ref'. 
        Use SQL queries to generate accurate results from these tables.
    """),
    ("user", "{question}")
])

# Create SQL Agent
agent_executor_SQL_v1 = create_sql_agent(
    llm=llm,
    toolkit=sql_toolkit,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=False,
    max_execution_time=100,
    max_iterations=1000
)

def sql_chatbot(question):
    try:
        # Get SQL Agent response
        resp = agent_executor_SQL_v1.invoke(prompt.format_prompt(question=question))
        text_output = resp['output']
        return text_output
    except Exception as e:
        return f"An error occurred: {str(e)}"
