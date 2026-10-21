import streamlit as st
from google import genai

# Cấu hình giao diện
st.set_page_config(page_title="Chatbot AI", page_icon="🤖", layout="centered")
st.title("🤖 Chatbot AI của tôi")
st.caption("Trợ lý AI thông minh tích hợp Google Gemini")

# Lấy API Key
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("⚠️ Chưa cấu hình GEMINI_API_KEY trong Secrets!")
    st.stop()

# Lưu kết nối để phản hồi nhanh
@st.cache_resource
def get_client(key):
    return genai.Client(api_key=key)

client = get_client(api_key)

# Quản lý lịch sử chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Xử lý tin nhắn
if prompt := st.chat_input("Hỏi tôi bất cứ điều gì..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gửi 10 câu gần nhất
    formatted_contents = [
        {
            "role": "model" if msg["role"] == "assistant" else "user",
            "parts": [{"text": msg["content"]}]
        }
        for msg in st.session_state.messages[-10:]
    ]

    with st.chat_message("assistant"):
        try:
            # Dùng tên model mới nhất gemini-3.8-flash
            response_stream = client.models.generate_content_stream(
                model="gemini-3.8-flash",
                contents=formatted_contents,
            )
            full_response = st.write_stream(
                chunk.text for chunk in response_stream if chunk.text
            )
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Lỗi: {e}")
