import streamlit as st
import requests
from bs4 import BeautifulSoup

# Set Streamlit page config
st.set_page_config(page_title="📝 Content Writer AI", layout="wide")

# Title and description
st.title("📝 AI Content Writer with SEO & Humanizer")
st.markdown("Generate high-quality, SEO-optimized, and human-like content in seconds.")

# Input fields
topic = st.text_input("📌 Topic", placeholder="e.g., Bedrooms around the world")
content_type = st.selectbox("📄 Content Type", ["Blog", "Product Description", "Marketing Copy", "Listicle"])
tone = st.selectbox("🎤 Tone", ["Friendly", "Professional", "Witty", "Conversational", "Persuasive"])
word_count = st.slider("✍️ Word Count", min_value=100, max_value=1000, step=100, value=500)
seo_keywords = st.text_input("🔍 SEO Keywords (comma-separated)", placeholder="bedroom furniture, sleep health, side tables")
goal_summary = st.text_area("🎯 What is this content trying to achieve? (optional)", 
                            placeholder="e.g., Educate readers about bedroom design trends while boosting SEO for 'bedroom furniture'")
ref_links = st.text_area("🌐 Reference URLs (optional, comma-separated)", 
                         placeholder="https://example.com/article1, https://example.com/blog2")

# Optional humanizer
humanize = st.checkbox("🧠 Humanize the content (make it feel more natural)", value=True)

# Helper to extract content from URLs
def extract_text_from_url(url):
    try:
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text() for p in paragraphs)
        return text[:1000]  # Limit to 1000 characters
    except Exception:
        return f"[Could not extract text from {url}]"

# Prompt builder
def build_prompt(topic, tone, word_count, content_type, seo_keywords, ref_links, goal_summary):
    base = f"Write a {word_count}-word {content_type.lower()} on the topic: '{topic}'.\n"
    tone_line = f"Use a {tone.lower()} tone.\n"
    seo_line = f"Include these SEO keywords naturally: {seo_keywords}.\n" if seo_keywords else ""
    style_line += (
    "Before starting the content, add a short personal anecdote or opinion to make it feel personal. "
    "Also add a summary or closing remark at the end that uses an idiom or common expression."
      
    "Write like a human, not a robot. Use contractions (don't, can't), rhetorical questions, emotional phrases, idioms, casual slang, and some personal voice. "
    "Avoid perfect grammar — make it feel natural, like a blogger or storyteller wrote it.\n"
                  )
    
    



    context = ""
    if ref_links and ref_links.strip():
        urls = [u.strip() for u in ref_links.split(",") if u.strip()]
        if urls:
            st.info("⏳ Extracting content from reference links...")
            ref_texts = [extract_text_from_url(u) for u in urls]
            context = "\nHere are some reference ideas and info from provided links:\n" + "\n".join(ref_texts) + "\n"

    goal_line = ""
    if goal_summary and goal_summary.strip():
        goal_line = f"\nThe goal of this content is: {goal_summary.strip()}.\n"

    return context + base + tone_line + seo_line + goal_line + style_line

# Chat function using OpenRouter API
def chat_with_model(messages, model="mistral", api_key=""):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://your-app-name.streamlit.app",
        "Content-Type": "application/json"
    }
    payload = {
    "model": model,
    "messages": messages,
    "temperature": 1.0  # increase from 0.7 to 1.0 for more variation
            }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()
   

# Generate content
if st.button("🚀 Generate Content"):
    with st.spinner("Generating your content..."):
        try:
            api_key = st.secrets["OPENROUTER_API_KEY"]
            model = "mistralai/mistral-7b-instruct"  # Or replace with your preferred model

            # 1st generation step
            prompt = build_prompt(topic, tone, word_count, content_type, seo_keywords, ref_links, goal_summary)
            messages = [
                {"role": "system", "content": "You are a helpful and skilled SEO content writer."},
                {"role": "user", "content": prompt}
            ]
            result = chat_with_model(messages, model=model, api_key=api_key)
            content = result["choices"][0]["message"]["content"]

            # Optional humanization pass
            if humanize:
                st.info("✨ Humanizing the content...")
                humanizer_prompt = [
                                     {
                                       "role": "system",
                                          "content": "You are a skilled editor. Rewrite AI-generated content to sound like it was written by a real person — casual, with personality, slang, varied sentence lengths, rhetorical questions, light sarcasm, and minor imperfections."
                                     },
                                    {
                                             "role": "user",
                                               "content": f"Make this sound human-written (add casual tone, unpredictability, idioms, emotional cues):\n\n{content}"
                                      }
                                   ]

                result = chat_with_model(humanizer_prompt, model=model, api_key=api_key)
                content = result["choices"][0]["message"]["content"]

            st.success("✅ Content Generated!")
            st.text_area("✍️ Your Content", value=content, height=400)

        except Exception as e:
            st.error(f"❌ Error: {e}")

