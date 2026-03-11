import streamlit as st
import google.generativeai as genai
import random
from fpdf import FPDF
import os
from dotenv import load_dotenv


# --- 1. Configuration & Security ---
# Load variables from .env (for local development)
load_dotenv()

# Safe check for API Key (Checks local .env first, then Streamlit Secrets)
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    try:
        # This allows the app to work on Streamlit Cloud after deployment
        api_key = st.secrets["GOOGLE_API_KEY"]
    except Exception:
        api_key = None

if not api_key:
    st.error("⚠️ API Key not found. Please ensure it's in your .env file locally or Streamlit Secrets on Cloud.")
    st.stop()

# Configure Gemini (Stable version)
genai.configure(api_key=api_key)


# Safe check for API Key to prevent StreamlitSecretNotFoundError
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    try:
        # This will only run if st.secrets exists (like on Streamlit Cloud)
        api_key = st.secrets["GOOGLE_API_KEY"]
    except Exception:
        api_key = None

if not api_key:
    st.error("⚠️ API Key not found. Please ensure it's in your .env file locally or Streamlit Secrets on Cloud.")
    st.stop()

# Configure Gemini 2.5 Flash
genai.configure(api_key=api_key)

# Define model settings
generation_config = {
    "temperature": 0.75,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Initializing model
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash", 
    generation_config=generation_config,
)

# --- 2. Joke Generation Function ---
def get_joke():
    jokes = [
        "Why do Java developers wear glasses? Because they don't see sharp.",
        "Why don't programmers like nature? It has too many bugs.",
        "How many programmers does it take to change a light bulb? None, that's a hardware problem.",
        "Why did the developer go broke? Because he used up all his cache.",
        "Why was the computer cold? It left its Windows open."
    ]
    return random.choice(jokes)

# --- 3. Streamlit UI Setup ---
st.set_page_config(page_title="Flavour Fusion", page_icon="🍲")

st.title("RecepieMaster: AI-Powered Blog Generation") 
st.write("🤖 Hello! I'm recepieMaster, your friendly robot. Let’s create a fantastic recepie together!") 

# User Inputs
topic = st.text_input("Topic", placeholder="e.g., malai kofta")
word_count = st.number_input("Number of words", min_value=100, max_value=2000, value=555)

# --- 4. Recipe Generation Logic ---
if st.button("Generate recepie"):
    if topic:
        with st.status("Generating your recepie...", expanded=True) as status:
            st.write(f"⌛ While I work, here’s a joke: **{get_joke()}**")
            
            prompt = f"Write a professional and engaging recipe blog about {topic} in approximately {word_count} words. Include prep time, cook time, ingredients, and step-by-step instructions."
            
            try:
                response = model.generate_content(prompt)
                recipe_text = response.text
                status.update(label="🎉 Your recepie is ready!", state="complete", expanded=False)
                
                st.markdown(recipe_text)
                st.divider()
                
                # --- 5. Robust Professional Export Features ---
                col1, col2 = st.columns(2)
                
                with col1:
                    try:
                        # Attempt native clipboard (Streamlit 1.40+)
                        st.copy_to_clipboard(recipe_text)
                        st.success("Recipe text copied to clipboard!")
                    except AttributeError:
                        # Fallback for environment/path issues
                        st.info("📋 Click the icon in the box below to copy:")
                        st.code(recipe_text, language="markdown")

                with col2:
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    # Clean text for PDF compatibility
                    clean_text = recipe_text.encode('latin-1', 'ignore').decode('latin-1')
                    pdf.multi_cell(0, 10, clean_text)
                    pdf_data = pdf.output(dest='S').encode('latin-1')
                    
                    st.download_button(
                        label="📥 Download as PDF",
                        data=pdf_data,
                        file_name=f"{topic}_recipe.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a topic first!")
