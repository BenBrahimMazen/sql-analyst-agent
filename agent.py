from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from database import run_query, get_schema
import re
import pandas as pd

# Load schema once at startup
SCHEMA = get_schema()

SYSTEM_PROMPT = f"""
You are an expert financial data analyst assistant.
You have access to a SQLite finance database with the following schema:

{SCHEMA}

RULES:
1. When the user asks a question, generate a valid SQLite SQL query to answer it.
2. Always wrap your SQL query in a ```sql code block.
3. After the SQL block, write a brief plain-English interpretation of what the query does.
4. Use only the tables and columns shown in the schema above.
5. For date filtering, the transaction_date and date columns are in YYYY-MM-DD format.
6. Never make up column names or tables that don't exist.
7. Keep your SQL clean and efficient.

Example format:
```sql
SELECT ticker, SUM(total_value) as total
FROM transactions
WHERE transaction_type = 'BUY'
GROUP BY ticker
ORDER BY total DESC
LIMIT 5;
```
This query finds the top 5 most purchased stocks by total value spent.
"""

def extract_sql(text: str) -> str | None:
    """Pull the SQL query out of the LLM response."""
    pattern = r"```sql\s*(.*?)```"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def ask_agent(user_question: str, chat_history: list) -> dict:
    """
    Send a question to the agent.
    Returns a dict with: response_text, sql, dataframe, error
    """
    llm = ChatOllama(model="llama3.1", temperature=0)

    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    # Include chat history for context
    for entry in chat_history:
        messages.append(HumanMessage(content=entry["user"]))
        messages.append(SystemMessage(content=entry["assistant"]))

    messages.append(HumanMessage(content=user_question))

    try:
        response = llm.invoke(messages)
        response_text = response.content

        sql = extract_sql(response_text)
        df = None
        error = None

        if sql:
            try:
                df = run_query(sql)
            except ValueError as e:
                error = str(e)
        else:
            error = "No SQL query was generated for this question."

        return {
            "response_text": response_text,
            "sql": sql,
            "dataframe": df,
            "error": error
        }

    except Exception as e:
        return {
            "response_text": "Sorry, I encountered an error.",
            "sql": None,
            "dataframe": None,
            "error": str(e)
        }