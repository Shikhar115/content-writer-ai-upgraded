import streamlit as st
import requests

st.set_page_config(page_title="AI Content Writer", layout="centered")
st.title("📝 AI Content Writer (with SEO!)")
st.caption("Powered by OpenRouter + Mistral 7B")

# Sidebar config
with st.sidebar:
    st.header("🔐 Settings")
    api_key = st.secrets.get("api_key", st.text_input("OpenRouter API Key", type="password"))
    model = "mistral/mistral-7b-instruct"
    st.markdown("[Get your API key here](https://openrouter.ai/)")

# User inputs
topic = st.text_input("📌 Blog topic")
content_type = st.selectbox("🗂️ Content Type", ["Blog", "LinkedIn Post", "Tweet Thread", "YouTube Script"])
tone = st.selectbox("🎙️ Tone", ["Professional", "Casual", "Witty", "Formal", "Friendly"])
word_count = st.slider("✍️ Word Count", 100, 1000, 500, step=100)
seo_keywords = st.text_input("🔎 SEO Keywords (comma-separated)", placeholder="e.g., bedroom furniture, sleep health")

# Prompt generator
def build_prompt(topic, tone, word_count, content_type, seo_keywords):
    base = f"Write a {word_count}-word {content_type.lower()} on the topic: '{topic}'.\n"
    tone_line = f"Use a {tone.lower()} tone.\n"
    seo_line = f"Include these SEO keywords naturally: {seo_keywords}.\n" if seo_keywords else ""
    style_line = "Make it engaging and structured with headings or bullet points where suitable.\n"
    return base + tone_line + seo_line + style_line

# Generate content
def generate_content(prompt, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful AI content writer with SEO knowledge."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        res.raise_for_status()
        return res.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ Error: {str(e)}"

# UI interaction
if st.button("✏️ Generate Content"):
    if not topic or not api_key:
        st.warning("Please provide a topic and your API key.")
    else:
        with st.spinner("Creating SEO-optimized content..."):
            prompt = build_prompt(topic, tone, word_count, content_type, seo_keywords)
            output = generate_content(prompt, api_key)
            st.markdown("### 🧾 Generated Content")
            st.write(output)
            st.download_button("📥 Download Content", output, file_name="content.txt")
