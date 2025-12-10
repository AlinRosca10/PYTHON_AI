# ai_utils.py
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_summary_ai(text: str, max_len=120):
    """
    Generează un rezumat scurt, calm, în stil calmcode.
    Fallback automat dacă API-ul pică.
    """
    prompt = f"""
    Rezumă următorul text în maximum {max_len} caractere.
    Fă-l clar, calm, concis și fără detalii inutile.
    Fără markdown. Fără listă.

    Text:
    {text}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",   # sau modelul tău preferat
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80,
            temperature=0.3,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("[WARN] AI summary failed:", e)
        return fallback_summary(text, max_len)


def fallback_summary(text, max_len):
    text = text.replace("\n", " ")
    if len(text) > max_len:
        return text[:max_len].rsplit(" ", 1)[0] + "..."
    return text