# embeddings/router.py — route questions to RAG vs general LLM
from groq import Groq
from dotenv import load_dotenv
import os
from embeddings.memory import is_memory_question, extract_name

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def classify_question(question: str) -> str:
  if is_memory_question(question):
    return "memory"
  """
  Route question to correct handler:
  - "health"   → RAG pipeline (search knowledge base)
  - "general"  → LLM directly (no RAG needed)
  """
  response = client.chat.completions.create(
      model="llama-3.1-8b-instant",   # fast cheap model for routing
      messages=[
          {
              "role": "system",
              "content": (
                  "Classify this question as either 'health' or 'general'.\n\n"
                  "health: questions about diseases, symptoms, medicines, "
                  "prevention, treatment, body, nutrition, hospitals\n"
                  "general: greetings, personal info, math, weather, "
                  "unrelated topics, 'who am I', 'what is your name'\n\n"
                  "Reply with ONLY one word: health or general"
              )
          },
          {"role": "user", "content": question}
      ],
      temperature=0.0,
      max_tokens=5
  )
  result = response.choices[0].message.content.strip().lower()
  return "health" if "health" in result else "general"


def answer_general(question: str, language_name: str, history: list = []) -> str:
    """Answer general/conversational questions directly without RAG."""
    messages = [
        {
            "role": "system",
            "content": (
                f"You are HealthBridge Africa, a friendly health assistant. "
                f"Answer in {language_name}. "
                f"Use conversational style, emojis, and be concise. "
                f"Use conversation history to remember user's name and details. "
                f"remember what user told you in the past and use it to answer questions about them. "
                f"don't ask for user's name, if they told you before, just use it. "
                f"if user asks for your name, respond with 'I am HealthBridge Africa, your friendly health assistant."
                f"not only answer the question, but also try to be engaging and build rapport. "
                f"when you try to remember user's name, use the following format: 'I think your name is [name], is that right?' "
                f"remember, if user asks questions about health, you should still answer them, but also try to gently guide the conversation back to health topics. "
                f"remember the language of the conversation and answer in that language. "
                f"be perfect to detect and use the language of the user, if you are not sure, use the language of the last message from the user. "
                f"For non-health questions, be friendly and brief. "
                f"Gently guide the user back to health topics."
            )
        }
    ]
    for msg in history[-10:]:
        messages.append(msg)
    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=200,
        temperature=0.7
    )
    return response.choices[0].message.content