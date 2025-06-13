import streamlit as st
import requests
from bs4 import BeautifulSoup

# Page config
st.set_page_config(page_title="📝 Content Writer AI", layout="wide")
st.title("📝 AI Content Writer with SEO & Human Touch")

# Inputs
topic = st.text_input("📌 Topic", placeholder="e.g., Bedrooms around the world")
content_type = st.selectbox("📄 Content Type", ["Blog", "Product Description", "Marketing Copy", "Listicle"])
tone = st.selectbox("🎤 Tone", ["Friendly", "Professional", "Witty", "Conversational", "Persuasive"])
word_count = st.slider("✍️ Word Count", min_value=100, max_value=1000, step=100, value=500)
seo_keywords = st.text_input("🔍 SEO Keywords (comma-separated)", placeholder="bedroom furniture, sleep health, side tables")
goal_summary = st.text_area("🎯 Content Goal (optional)", placeholder="What should this article accomplish?")
ref_links = st.text_area("🌐 Reference URLs (optional, comma-separated)", placeholder="https://example.com/article1, https://example.com/blog2")
humanize = st.checkbox("🧠 Humanize the content (more natural, emotional, less robotic)", value=True)

# Function to scrape reference content
def extract_text_from_url(url):
    try:
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text() for p in paragraphs)
        return text[:1000]  # limit length
    except Exception:
        return f"[Could not extract text from {url}]"

# Build prompt for generation
def build_prompt(topic, tone, word_count, content_type, seo_keywords, ref_links, goal_summary):
    base = f"Write a {word_count}-word {content_type.lower()} about '{topic}'.\n"
    tone_line = f"Use a {tone.lower()} tone.\n"
    seo_line = f"Naturally include these SEO keywords: {seo_keywords}.\n" if seo_keywords else ""
    goal_line = f"Main goal: {goal_summary.strip()}.\n" if goal_summary else ""

    style_line = (
        "Write like a clever human: include personal touches, rhetorical questions, minor imperfections, idioms, contractions, and slight humor. "
        "Make it engaging with natural flow, varied sentence lengths, and emotional language.\n"
    )

    context = ""
    if ref_links and ref_links.strip():
        urls = [u.strip() for u in ref_links.split(",") if u.strip()]
        if urls:
            st.info("⏳ Pulling insights from reference links...")
            ref_texts = [extract_text_from_url(u) for u in urls]
            context = "\nHere are reference notes from the provided links:\n" + "\n".join(ref_texts) + "\n"

    return context + base + tone_line + seo_line + goal_line + style_line

# Call OpenRouter API
def chat_with_model(messages, model="openchat/openchat-3.5", api_key="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"):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-streamlit-app.streamlit.app"
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 1.0  # More randomness/human-like
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

# Generate content
if st.button("🚀 Generate Content"):
    with st.spinner("Crafting your content..."):
        try:
            api_key = st.secrets["OPENROUTER_API_KEY"]
            model = "openchat/openchat-3.5"
            prompt = build_prompt(topic, tone, word_count, content_type, seo_keywords, ref_links, goal_summary)

            messages = [
                {"role": "system", "content": "You are a creative, funny, and relatable SEO content writer."},
                {"role": "user", "content": prompt}
            ]

            result = chat_with_model(messages, model=model, api_key=api_key)
            content = result["choices"][0]["message"]["content"]

            # Optional humanizer step
            if humanize:
                st.info("✨ Humanizing the writing further...")
                humanizer_prompt = [
                    {"role": "system", "content": "You're an editor rewriting content to sound natural, human, slightly imperfect, and emotionally engaging."},
                    {"role": "user", "content": f"Rewrite this text to feel more like a human wrote it:\n\n{content}"}
                ]
                result = chat_with_model(humanizer_prompt, model=model, api_key=api_key)
                content = result["choices"][0]["message"]["content"]

            st.success("✅ Content Generated!")
            st.text_area("✍️ Your Final Content", value=content, height=500)

        except Exception as e:
            st.error(f"❌ Error: {e}")
