# studying_project-
YouTube Transcript Summarizer & Q&A API
=======================================

A FastAPI application that allows you to:
- Extract transcripts from YouTube videos 
- Summarize the transcript
- Extract the main points
- Chat with the transcript using natural language questions

---------------------------------------
how to start
---------------------------------------

1. Clone the Repository
-----------------------
git clone https://github.com/your-username/yt-transcript-groq-api.git
cd yt-transcript-groq-api

2. (Optional) Create & Activate a Virtual Environment
------------------------------------------------------
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows

3. Install Required Packages
----------------------------
pip install -r requirements.txt

4. Set Your API Key
-------------------
Create a file called `.env` in the root directory and add your Groq API key:

GROQ_API_KEY=your_groq_api_key_here

5. Run the Server
-----------------
uvicorn main:app --reload

Open in browser: http://localhost:8000/docs

---------------------------------------
Available API Endpoints
---------------------------------------

1. POST /getting_script
-----------------------
Get YouTube video transcript in the desired language.

Request Body (JSON):
{
  "input_link": "https://www.youtube.com/watch?v=abcd1234",
  "language": "en"
}

Response: Returns transcript text and video info.

2. POST /summarize
------------------
Summarize any given text using the LLaMA model.

Request Body (JSON):
{
  "input_text": "Your transcript or paragraph here"
}

Response: A summarized version of the input.

3. POST /extract_main_points
----------------------------
Extract numbered key points from any text.

Request Body (JSON):
{
  "input_text": "Your transcript or paragraph here"
}

Response: Key points in a numbered list.

4. POST /chat
-------------
Ask a question based on a provided text. The model will only answer if the question is relevant to the context.

Request Body (JSON):
{
  "input_text": "Text to use as context",
  "question": "What is this video about?"
}

Response: The model's answer in the same language as the question.

5. GET /
-------
Returns a simple welcome message.
