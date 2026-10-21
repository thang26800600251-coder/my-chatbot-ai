import streamlit as st
from google import genai
from google.genai import types

# Cấu hình giao diện
st.set_page_config(page_title="Chatbot AI của Thắng", page_icon="⚡", layout="centered")
st.title("⚡ Chatbot AI của Thắng")
st.caption("Trợ lý AI phản hồi")

# Lấy API Key từ Secrets
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("⚠️ Chưa cấu hình GEMINI_API_KEY trong Secrets!")
    st.stop()

# Cache kết nối Client để không tạo lại kết nối mỗi lần nhắn
@st.cache_resource
def get_client(key):
    return genai.Client(api_key=key)

client = get_client(api_key)

# Quản lý lịch sử trò chuyện
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Xử lý tin nhắn người dùng
if prompt := st.chat_input("Hỏi tôi bất cứ điều gì..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # TỐI ƯU 1: Chỉ đọc 4 câu hội thoại gần nhất để xử lý dữ liệu nhanh nhất
    recent_messages = st.session_state.messages[-4:]
    formatted_contents = [
        {
            "role": "model" if msg["role"] == "assistant" else "user",
            "parts": [{"text": msg["content"]}]
        }
        for msg in recent_messages
    ]

    # TỐI ƯU 2: Cấu hình ép AI trả lời ngắn gọn, trực diện
    config = types.GenerateContentConfig(
        system_instruction="Bạn là trợ lý AI siêu tốc. Luôn trả lời ngắn gọn, đi thẳng vào vấn đề, không rườm rà hay chào hỏi thừa thải.",
        max_output_tokens=500,  # Giới hạn độ dài giúp sinh chữ siêu nhanh
        temperature=0.5,
    )

    with st.chat_message("assistant"):
        try:
            # Phát luồng chữ thời gian thực
            response_stream = client.models.generate_content_stream(
                model="gemini-3.8-flash",
                contents=formatted_contents,
                config=config,
            )
            full_response = st.write_stream(
                chunk.text for chunk in response_stream if chunk.text
            )
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Lỗi: {e}")
