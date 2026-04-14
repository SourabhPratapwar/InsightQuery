# InsightQuery

InsightQuery is a simple data analytics app that lets you query your data using plain English instead of writing SQL manually. It takes a natural language question, 
converts it into a SQL query, runs it on your data, and shows the results along with basic visualizations.

The goal of this project is to make data exploration faster and more intuitive, especially for users who are not comfortable writing SQL.
## What it does
- Converts natural language questions into SQL queries
- Runs queries on a SQLite database
- Lets you upload Excel files and query them directly
- Automatically validates and fixes SQL when possible
- Shows results in table and chart form
- Generates short insights based on the result
- Suggests questions based on your dataset
- Keeps track of recent queries

## Tech Stack
- Python
- Streamlit (UI)
- SQLite (database)
- Sentence Transformers (for schema embeddings)
- Ollama with Mistral (for LLM-based query generation)
- Pandas (data handling)

## Project Structure
- app.py                     # Main Streamlit app
- llm.py                     # LLM logic (SQL generation, suggestions)
- rag.py                     # Schema retrieval using embeddings
- executor.py                # SQL execution
- validator.py               # SQL validation and safety checks
- query_service.py           # End-to-end query pipeline
- data_service.py            # Excel to SQLite conversion
- state_service.py           # Session state management
- dashboard.py               # Chart rendering
- components.py              # UI helpers (optional)
- setup_db.py                # Sample database setup

## Running the app
Start the Streamlit app:
streamlit run app.py

## LLM setup (important)
This project uses Ollama locally for generating SQL queries.
Make sure Ollama is installed and running:
ollama run mistral

The app expects Ollama to be available at:
http://localhost:11434

## How to use
1. Upload an Excel file (or use the default database)
2. Type a question in plain English
3. Click the "Run" button
4. View:
   - Query results
   - Generated SQL
   - Chart visualization
   - Insights

## Example questions
- Which cities have the highest average order value?
- What is the total revenue by month?
- Who are the top 5 customers?
- Show sales trend over time
  
## Notes
- Only SELECT queries are allowed for safety
- Queries are automatically limited to avoid heavy loads
- SQL is validated and corrected when possible
- Schema-aware retrieval improves query accuracy
  
## Limitations
- UI is built with Streamlit, so layout customization is limited
- Depends on local LLM (Ollama), not cloud-based
- Works best with clean, structured datasets

## Future improvements
- Chat-style interface
- More advanced visualizations
- Export results to CSV
- Better query explanations
- Deployment as a web app

## License
This project is for learning and demonstration purposes.
