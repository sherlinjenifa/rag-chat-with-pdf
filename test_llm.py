from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Explain RAG in 2 simple lines",
)
print(response.text)