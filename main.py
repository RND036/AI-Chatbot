from groq import Groq
import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

# give title to the page
st.title("🌾 Agricultural AI Assistant")

# Agricultural system prompt
AGRICULTURE_SYSTEM_PROMPT = """You are an expert agricultural AI assistant. Your knowledge covers:
- Crop cultivation and farming techniques
- Plant diseases and pest management
- Soil health and fertilization
- Weather and climate impacts on agriculture
- Sustainable farming practices
- Agricultural machinery and technology
- Livestock management
- Food production and processing
- Agricultural economics and market trends

You should only respond to agriculture-related questions. If asked about non-agricultural topics, politely redirect the conversation back to farming and agriculture.

Always provide practical, actionable advice that farmers can implement. Include relevant details about timing, quantities, and specific techniques when applicable."""

# initializing models
if 'model' not in st.session_state:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("GROQ_API_KEY not found. Please set it in your .env file or environment variables.")
        st.stop()
    st.session_state['model'] = Groq(api_key=api_key)

if 'messages' not in st.session_state:
    # Initialize with system prompt and greeting
    st.session_state['messages'] = [
        {"role": "system", "content": AGRICULTURE_SYSTEM_PROMPT},
        {"role": "assistant", "content": "🌾 Welcome to your Agricultural AI Assistant! 🌱\n\nI'm here to help you with all your farming and agriculture questions. Whether you need advice on:\n\n• Crop cultivation and planting\n• Disease and pest management\n• Soil health and fertilization\n• Weather and climate concerns\n• Sustainable farming practices\n• Agricultural technology\n• Livestock management\n\nJust ask me anything! You can also use the quick topic buttons in the sidebar for common questions.\n\nHow can I help you grow better today? 🚜"}
    ]

# create sidebar to adjust model parameters
st.sidebar.title("Model Parameters")
temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=2.0, value=0.7, step=0.1)
max_tokens = st.sidebar.slider("Max Tokens", min_value=1, max_value=4096, value=512)

# Agriculture-specific quick prompts
st.sidebar.title("Quick Agriculture Topics")
quick_prompts = {
    "🌱 Crop Diseases": "What are common crop diseases and how to prevent them?",
    "🚜 Farming Techniques": "What are sustainable farming techniques I should know?",
    "🌾 Soil Health": "How can I improve my soil health naturally?",
    "🐛 Pest Control": "What are organic pest control methods?",
    "💧 Irrigation": "What are efficient irrigation techniques?",
    "🌤️ Weather Impact": "How does weather affect crop growth?",
    "🥕 Vegetable Farming": "Best practices for vegetable farming?",
    "🌿 Organic Farming": "How to transition to organic farming?"
}

for topic, prompt in quick_prompts.items():
    if st.sidebar.button(topic):
        st.session_state['messages'].append({"role": "user", "content": prompt})

# update the interface with previous messages (skip system message)
for message in st.session_state['messages'][1:]:  # Skip system prompt
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# create the chat interface
if prompt := st.chat_input("Ask me anything about agriculture, farming, or crops..."):
    st.session_state['messages'].append({"role": "user", "content": prompt})
    with st.chat_message('user'):
        st.markdown(prompt)

    # get response from the model 
    with st.chat_message("assistant"):
        # Build chat completion call
        client = st.session_state['model']
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": msg["role"], "content": msg["content"]}
                for msg in st.session_state["messages"]
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )

        # Display and collect streamed output
        def response_generator():
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        full_response = st.write_stream(response_generator())

    st.session_state['messages'].append({"role": "assistant", "content": full_response})

# Add some helpful info in the sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 🌾 About This Assistant")
st.sidebar.markdown("""
This AI assistant specializes in:
- **Crop Management**: Planting, growing, harvesting
- **Disease & Pest Control**: Identification and treatment
- **Soil & Fertilization**: Soil health and nutrient management
- **Sustainable Practices**: Organic and eco-friendly methods
- **Weather & Climate**: Impact on farming decisions
- **Agricultural Technology**: Modern farming tools and techniques
""")

