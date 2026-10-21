import streamlit as st
from google import genai

# Cấu hình giao diện
st.set_page_config(page_title="Chatbot AI của Thắng", page_icon="⚡", layout="centered")
st.title("⚡ Chatbot AI của Thắng")
st.caption("Trợ lý AI phản hồi siêu tốc")

# Lấy API Key
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("⚠️ Chưa cấu hình GEMINI_API_KEY trong Secrets!")
    st.stop()

# Cache kết nối Client
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

# Xử lý khi người dùng nhắn tin
if prompt := st.chat_input("Hỏi tôi bất cứ điều gì..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Đóng gói 6 câu thoại gần nhất
    recent_messages = st.session_state.messages[-6:]
    formatted_contents = [
        {
            "role": "model" if msg["role"] == "assistant" else "user",
            "parts": [{"text": msg["content"]}]
        }
        for msg in recent_messages
    ]

    with st.chat_message("assistant"):
        try:
            # Dùng đúng tên mô hình gemini-3.8-flash chuẩn
            response_stream = client.models.generate_content_stream(
                model="gemini-3.8-flash",
                contents=formatted_contents,
            )

            # Phát luồng chữ gõ trực tiếp
            full_response = st.write_stream(
                chunk.text for chunk in response_stream if chunk.text
            )
            
            if full_response:
                st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Lỗi: {e}")
