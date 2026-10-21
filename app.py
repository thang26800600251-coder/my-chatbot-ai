import streamlit as st
from google import genai

# Cấu hình giao diện trang web
st.set_page_config(page_title="Chatbot AI", page_icon="🤖", layout="centered")
st.title("🤖 Chatbot AI của tôi")
st.caption("Trợ lý AI thông minh tích hợp Google Gemini")

# Lấy API Key từ Secrets
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ Chưa cấu hình GEMINI_API_KEY trong Secrets!")
    st.stop()

# TỐI ƯU 1: Caching Client giúp giữ nguyên kết nối, không tạo lại ở mỗi câu hỏi
@st.cache_resource
def get_client(key):
    return genai.Client(api_key=key)

client = get_client(api_key)

# Khởi tạo lịch sử chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lịch sử trò chuyện
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Xử lý khi người dùng nhập tin nhắn
if prompt := st.chat_input("Hỏi tôi bất cứ điều gì..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # TỐI ƯU 2: Chỉ gửi 10 tin nhắn gần nhất để giảm thời gian xử lý dữ liệu
    recent_messages = st.session_state.messages[-10:]
    formatted_contents = [
        {
            "role": "model" if msg["role"] == "assistant" else "user",
            "parts": [{"text": msg["content"]}]
        }
        for msg in recent_messages
    ]

    with st.chat_message("assistant"):
        try:
            # TỐI ƯU 3: Sử dụng model gemini-2.0-flash cho tốc độ xử lý nhanh nhất
            response_stream = client.models.generate_content_stream(
                model="gemini-2.0-flash",
                contents=formatted_contents,
            )

            full_response = st.write_stream(
                chunk.text for chunk in response_stream if chunk.text
            )
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Lỗi: {e}")
