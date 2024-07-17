import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Configuration for the generative model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

chat_session = model.start_chat(history=[])

# Define input parameters
class_name = "10th Grade"
subject_name = "Mathematics"
question_type = "objective"

# Construct the prompt
prompt = f"Generate a {question_type} question for {class_name} students studying {subject_name}."

# Send the prompt to the model and get the generated question
response = chat_session.send_message(prompt)
generated_question = response.text
print(generated_question)
