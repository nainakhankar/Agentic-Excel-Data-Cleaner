🤖 Agentic Excel Data Cleaner
An AI-powered web app built with Streamlit, LangChain, and Google Gemini to clean messy Excel files in just a few clicks.

📌 Features
Upload any Excel file (.xlsx, .xls)

Remove missing values automatically

Eliminate duplicate rows

Get instant dataset summary (shape, missing values, duplicates)

Download cleaned Excel file instantly

Powered by Agentic AI to execute cleaning steps dynamically

🖥️ Tech Stack
Python 3.10+

Streamlit – for the interactive UI

Pandas – for data processing

LangChain – for the agent architecture

Google Gemini API – for the AI reasoning

dotenv – for environment variable management

🚀 How It Works
Upload your messy Excel file via the web interface.

AI Agent runs a cleaning sequence:

drop_all_na_rows → Removes rows with missing data.

remove_all_duplicate_rows → Removes duplicate rows.

get_dataframe_info → Summarizes the cleaned data.

Download your cleaned Excel file ready for analysis.

📦 Installation
1️⃣ Clone the repository
bash
Copy
Edit
git clone https://github.com/your-username/agentic-excel-data-cleaner.git
cd agentic-excel-data-cleaner
2️⃣ Create a virtual environment & activate it
bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
3️⃣ Install dependencies
bash
Copy
Edit
pip install -r requirements.txt
4️⃣ Set up environment variables
Create a .env file in the root directory:

ini
Copy
Edit
GOOGLE_API_KEY=your_google_gemini_api_key
5️⃣ Run the app
bash
Copy
Edit
streamlit run app.py
🧪 Testing with Sample Data
We’ve included a large uncleaned Excel file with 5,000+ rows, missing values, and duplicates for testing:
uncleaned_large_excel.xlsx