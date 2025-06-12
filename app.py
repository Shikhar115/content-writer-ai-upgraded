import streamlit as st
import requests
from bs4 import BeautifulSoup


st.set_page_config(page_title="AI Content Writer", layout="centered")
st.title("📝 AI Content Writer (with SEO!)")
st.caption("Powered by OpenRouter + Mistral 7B")

#link_context
def extract_text_from_url(url):
    try:
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text() for p in paragraphs)
        return text[:1000]  # Limit to first 1000 chars to keep token usage low
    except Exception as e:
        return f"[Could not extract text from {url}]"


# Sidebar config
with st.sidebar:
    st.header("🔐 Settings")
    if "api_key" in st.secrets:
        api_key = st.secrets["api_key"]
        st.success("✅ API Key loaded from st.secrets.")
    else:
        api_key = st.text_input("OpenRouter API Key", type="password")
        st.warning("⚠️ You can also store this in Streamlit secrets to avoid entering every time.")
    model = "mistralai/mistral-7b-instruct:free"
    st.markdown("[Get your API key here](https://openrouter.ai/)")


# User inputs
topic = st.text_input("📌 Blog topic")
content_type = st.selectbox("🗂️ Content Type", ["Blog", "LinkedIn Post", "Tweet Thread", "YouTube Script"])
tone = st.selectbox("🎙️ Tone", ["Professional", "Casual", "Witty", "Formal", "Friendly"])
word_count = st.slider("✍️ Word Count", 100, 1000, 500, step=100)
seo_keywords = st.text_input("🔎 SEO Keywords (comma-separated)", placeholder="e.g., bedroom furniture, sleep health")
ref_links = st.text_area("🌐 Reference URLs (optional, comma-separated)", placeholder="https://example.com/article1, https://example.com/blog2")
goal_summary = st.text_area("🎯 What is this content trying to achieve? (optional)", 
                            placeholder="e.g., Educate readers about bedroom design trends while boosting SEO for 'bedroom furniture'")



# Prompt builder
def build_prompt(topic, tone, word_count, content_type, seo_keywords, ref_links, goal_summary):
    base = f"Write a {word_count}-word {content_type.lower()} on the topic: '{topic}'.\n"
    tone_line = f"Use a {tone.lower()} tone.\n"
    seo_line = f"Include these SEO keywords naturally: {seo_keywords}.\n" if seo_keywords else ""
    style_line = "Make it engaging and structured with headings or bullet points where suitable.\n"

    # ✅ Safe context from ref_links
    context = ""
    if ref_links and ref_links.strip():
        urls = [u.strip() for u in ref_links.split(",") if u.strip()]
        if urls:
            st.info("⏳ Extracting content from reference links...")
            ref_texts = [extract_text_from_url(u) for u in urls]
            context = "\nHere are some reference ideas and info from provided links:\n" + "\n".join(ref_texts) + "\n"

    # ✅ Safe goal line
    goal_line = ""
    if goal_summary and goal_summary.strip():
        goal_line = f"\nThe goal of this content is: {goal_summary.strip()}.\n"

    return context + base + tone_line + seo_line + goal_line + style_line





# Content generation
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
    except requests.exceptions.RequestException as e:
        return f"❌ Error: {e}\n\n📌 Check your API key and model name. Also verify that your key is active at https://openrouter.ai/."

# UI interaction
if st.button("✏️ Generate Content"):
    if not topic or not api_key:
        st.warning("Please provide a topic and your API key.")
    else:
        with st.spinner("Creating SEO-optimized content..."):
            prompt = build_prompt(topic, tone, word_count, content_type, seo_keywords, ref_links, goal_summary)
            output = generate_content(prompt, api_key)
            st.markdown("### 🧾 Generated Content")
            st.write(output)
            st.download_button("📥 Download Content", output, file_name="content.txt")
