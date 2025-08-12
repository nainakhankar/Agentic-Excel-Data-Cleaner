import os
import streamlit as st
import pandas as pd
from io import BytesIO
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

# --- Load Environment Variables ---
load_dotenv()

# --- Configuration ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("Please set your GOOGLE_API_KEY environment variable in a .env file or Streamlit secrets.")
    st.stop()

# --- Global Agent & Memory Storage ---
if 'df' not in st.session_state:
    st.session_state.df = None
if 'agent_executor' not in st.session_state:
    st.session_state.agent_executor = None
if 'memory' not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# --- Data Cleaning Tools (Python Functions) ---

def load_excel_to_df(file_content: BytesIO, _: str = None) -> pd.DataFrame:
    """Loads an Excel file from BytesIO content into a pandas DataFrame."""
    try:
        st.session_state.df = pd.read_excel(file_content)
        return st.session_state.df
    except Exception as e:
        st.error(f"Error loading file: {e}. Please ensure it's a valid Excel file.")
        st.session_state.df = None
        return None

def drop_all_na_rows(_: str = None) -> str:
    """Drops all rows that contain any missing values."""
    if st.session_state.df is None:
        return "No DataFrame loaded."
    original_rows = st.session_state.df.shape[0]
    st.session_state.df.dropna(inplace=True)
    rows_dropped = original_rows - st.session_state.df.shape[0]
    return f"Rows with missing values dropped. {rows_dropped} rows removed. New shape: {st.session_state.df.shape}"

def remove_all_duplicate_rows(_: str = None) -> str:
    """Removes all duplicate rows from the DataFrame."""
    if st.session_state.df is None:
        return "No DataFrame loaded."
    original_rows = st.session_state.df.shape[0]
    st.session_state.df.drop_duplicates(inplace=True)
    rows_removed = original_rows - st.session_state.df.shape[0]
    return f"Duplicate rows removed. {rows_removed} rows removed. New shape: {st.session_state.df.shape}"

def get_dataframe_info(_: str = None) -> str:
    """Returns a string summary of the current DataFrame."""
    if st.session_state.df is None:
        return "No DataFrame loaded."
    df = st.session_state.df
    info = f"DataFrame Shape: {df.shape}\n"
    info += f"Missing Values (count per column):\n{df.isnull().sum().to_string()}\n"
    info += f"Duplicate Rows: {df.duplicated().sum()} (entire row duplicates)\n"
    return info

def save_df_to_excel(df: pd.DataFrame) -> BytesIO:
    """Saves the given DataFrame to an in-memory Excel file (BytesIO object) and returns it."""
    if df is None:
        return None
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return output

# --- LangChain Agent Setup ---
def initialize_data_cleaning_agent():
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.2
    )
    tools = [
        Tool(name="load_excel_to_df", func=load_excel_to_df, description="Loads an Excel file into the active DataFrame. Use ONLY when a new file is provided."),
        Tool(name="drop_all_na_rows", func=drop_all_na_rows, description="Drops any row with a missing value."),
        Tool(name="remove_all_duplicate_rows", func=remove_all_duplicate_rows, description="Removes any duplicate rows."),
        Tool(name="get_dataframe_info", func=get_dataframe_info, description="Provides a summary of the current DataFrame.")
    ]
    prompt_template = PromptTemplate.from_template(
        """
        You are an expert Data Cleaning Agent. Your primary goal is to help the user clean Excel file data.
        You have access to the following tools:

        {tools}

        Use the following format:

        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question

        Begin!

        {chat_history}
        Question: {input}
        {agent_scratchpad}
        """
    )
    agent = create_react_agent(llm, tools, prompt_template)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        memory=st.session_state.memory,
        handle_parsing_errors=True
    )
    st.session_state.agent_executor = agent_executor

# --- New function to handle the cleaning and saving process ---
def clean_and_save_data():
    if st.session_state.df is None:
        st.error("Please upload a file first.")
        return None
    
    with st.spinner("Agent is cleaning data..."):
        cleaning_request = (
            "I need to clean the data. First, I will call drop_all_na_rows "
            "to remove rows with missing data. Then I will call remove_all_duplicate_rows "
            "to remove any duplicate rows. Finally, I will call get_dataframe_info "
            "to see the final shape."
        )
        try:
            response = st.session_state.agent_executor.invoke({"input": cleaning_request})
            st.success("Data has been cleaned successfully!")
            st.info(f"Agent's cleaning report: {response['output']}")
            
            cleaned_df = st.session_state.df
            excel_data = save_df_to_excel(cleaned_df)
            return excel_data
        
        except Exception as e:
            st.error(f"An error occurred during cleaning: {e}")
            return None

# --- Streamlit UI ---
st.set_page_config(page_title="Agentic Excel Data Cleaner", layout="centered")
st.title("🤖 Agentic Excel Data Cleaner")
st.markdown("Upload an Excel file, and an AI agent will automatically clean it and prepare it for download.")

if st.session_state.agent_executor is None:
    initialize_data_cleaning_agent()

# File Uploader Section
st.header("1. Upload Your Excel File")
uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

if uploaded_file and st.session_state.df is None:
    st.session_state.memory.clear()
    file_content = BytesIO(uploaded_file.read())
    df = load_excel_to_df(file_content)
    if df is not None:
        st.success("File uploaded successfully!")
        st.info("The file is ready. Click the button below to have the agent clean it.")

if st.session_state.df is not None:
    st.header("2. Clean and Download")
    if st.button("Download Cleaned Excel"):
        cleaned_file_content = clean_and_save_data()
        
        if cleaned_file_content:
            st.download_button(
                label="Download Cleaned Excel",
                data=cleaned_file_content,
                file_name="cleaned_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
