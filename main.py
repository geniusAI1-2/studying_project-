from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
import os
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

load_dotenv()

app = FastAPI()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# request models
class GettingTheScript(BaseModel):
    input_link: str
    language: str

class SummarizationRequest(BaseModel):
    input_text: str

class MainPointsRequest(BaseModel):
    input_text: str

class ChatRequest(BaseModel):
    input_text: str
    question: str

# Endpoint for getting YouTube transcript
@app.post("/getting_script")
async def get_script(request: GettingTheScript):
    youtube_url = request.input_link
    language = request.language
    
    def extract_video_id(url):
        if 'youtu.be' in url:
            return url.split('/')[-1].split('?')[0]
        query = urlparse(url).query
        params = parse_qs(query)
        return params.get('v', [None])[0]

    def get_youtube_text(url, lang):
        try:
            video_id = extract_video_id(url)
            if not video_id:
                raise ValueError("Could not extract video ID from URL")
                
            # Try to get transcript in requested language
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
            except:
                print(f"No {lang} transcript available, trying English...")
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
                
            return " ".join([entry['text'] for entry in transcript])
        
        except Exception as e:
            print(f"Error: {str(e)}")
            return None

    text = get_youtube_text(youtube_url, language)

    if text:
        return {
            "status": "success",
            "video_url": youtube_url,
            "language": language,
            "transcript": text
        }
    else:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": "Failed to get transcript",
                "possible_reasons": [
                    "Video has no captions",
                    "Language not available",
                    "Invalid YouTube URL"
                ]
            }
        )
# Endpoint for summarization
@app.post("/summarize")
async def summarize(request: SummarizationRequest):
    input_text = request.input_text

    prompt = f"""
You are a professional summarization assistant. Your task is to summarize the following text in a clear, concise, and organized manner. Follow these rules:
1. The summary must be in the same language as the input text.
2. Do not add any information that is not in the original text.
3. Ensure the summary is comprehensive and captures all key points.

Examples:

Input (English):
Solar energy is one of the most important renewable energy sources. It is converted into electricity using solar panels, which absorb sunlight and convert it into electrical energy. Solar energy is used in many applications, such as generating electricity for homes and businesses, and powering small electronic devices.

Summary (English):
Solar energy is a key renewable energy source. It is converted into electricity via solar panels that absorb sunlight. It is used in various applications, including powering homes, businesses, and small electronic devices.

Input (Arabic):
تعتبر الطاقة الشمسية واحدة من أهم مصادر الطاقة المتجددة. يتم تحويل الطاقة الشمسية إلى كهرباء باستخدام الألواح الشمسية، والتي تعمل على امتصاص أشعة الشمس وتحويلها إلى طاقة كهربائية. تستخدم الطاقة الشمسية في العديد من التطبيقات مثل توليد الكهرباء للمنازل والشركات، وتشغيل الأجهزة الإلكترونية الصغيرة.

Summary (Arabic):
الطاقة الشمسية هي مصدر مهم للطاقة المتجددة. يتم تحويلها إلى كهرباء عبر الألواح الشمسية التي تمتص أشعة الشمس. تُستخدم في تطبيقات متنوعة مثل توليد الكهرباء للمنازل والشركات وتشغيل الأجهزة الإلكترونية الصغيرة.

Now, summarize the following text. Ensure the summary is in the same language as the input text and follows the rules above.

Input:
{input_text}

Summary:
"""

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
            stream=False,
        )
        summary = chat_completion.choices[0].message.content
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint for extracting main points
@app.post("/extract_main_points")
async def extract_main_points(request: MainPointsRequest):
    input_text = request.input_text
    prompt = f"""
    You are a professional assistant. Your task is to extract the main points from the following text and list them in a clear, numbered format (1, 2, 3, ...). Follow these rules:
    1. The main points must be in the same language as the input text.
    2. Do not add any information that is not in the original text.
    3. Ensure the points are concise and cover all key aspects of the text.

    Examples:

    Input (English):
    Solar energy is one of the most important renewable energy sources. It is converted into electricity using solar panels, which absorb sunlight and convert it into electrical energy. Solar energy is used in many applications, such as generating electricity for homes and businesses, and powering small electronic devices.

    Main Points (English):
    1. Solar energy is a key renewable energy source.
    2. It is converted into electricity via solar panels.
    3. It is used in various applications, including powering homes, businesses, and small electronic devices.

    Input (Arabic):
    تعتبر الطاقة الشمسية واحدة من أهم مصادر الطاقة المتجددة. يتم تحويل الطاقة الشمسية إلى كهرباء باستخدام الألواح الشمسية، والتي تعمل على امتصاص أشعة الشمس وتحويلها إلى طاقة كهربائية. تستخدم الطاقة الشمسية في العديد من التطبيقات مثل توليد الكهرباء للمنازل والشركات، وتشغيل الأجهزة الإلكترونية الصغيرة.

    Main Points (Arabic):
    1. الطاقة الشمسية هي مصدر مهم للطاقة المتجددة.
    2. يتم تحويلها إلى كهرباء عبر الألواح الشمسية.
    3. تُستخدم في تطبيقات متنوعة مثل توليد الكهرباء للمنازل والشركات.

    Now, extract the main points from the following text. Ensure the points are in the same language as the input text and follow the rules above.

    Input:
    {input_text}

    Main Points:
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
            stream=False,
        )
        main_points = chat_completion.choices[0].message.content
        return {"main_points": main_points}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint for chat with the user
@app.post("/chat")
async def chat(request: ChatRequest):
    input_text = request.input_text
    question = request.question

    prompt = f"""
    You are a knowledgeable and adaptive assistant. Your task is to answer the user's questions based on the following text. Follow these rules strictly:
    1. **Language Matching**: Respond in the same language as the question. If the question is in Arabic, respond in Arabic. If the question is in English, respond in English.
    2. **Contextual Awareness**: 
       - If the question is related to the provided text, answer it based on the text.
       - If the question is unrelated to the text, respond politely with:
         - "عذرًا، لا يمكنني الإجابة على هذا السؤال لأنه ليس في نفس سياق النص المقدم." (if the question is in Arabic).
         - "Sorry, I cannot answer this question as it is not within the context of the provided text." (if the question is in English).
    3. **Flexibility**: If the question is vague or ambiguous, ask for clarification or provide a general response based on the text.
    4. **Accuracy**: Do not add any information that is not in the original text. Your answer must be based solely on the provided text.

    Text:
    {input_text}
    Question:
    {question}
    Answer:
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
            stream=False,
        )
        answer = chat_completion.choices[0].message.content
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI "}
