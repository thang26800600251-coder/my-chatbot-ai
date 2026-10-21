import streamlit as st
from google import genai

# Cấu hình giao diện trang web
st.set_page_config(page_title="Chatbot AI", page_icon="🤖", layout="centered")
st.title("🤖 Chatbot AI của tôi")
st.caption("Trợ lý AI thông minh tích hợp Google Gemini")

# Lấy API Key từ cấu hình bí mật của Streamlit
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ Chưa cấu hình GEMINI_API_KEY! Hãy thêm API Key trong phần Secrets của Streamlit.")
    st.stop()

# Khởi tạo Client Gemini
client = genai.Client(api_key=api_key)

# Khởi tạo lịch sử chat trong session nếu chưa có
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lại lịch sử trò chuyện cũ
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Xử lý khi người dùng nhập tin nhắn
if prompt := st.chat_input("Hỏi tôi bất cứ điều gì..."):
    # 1. Lưu và hiển thị câu hỏi người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Đóng gói lịch sử trò chuyện
    formatted_contents = []
    for msg in st.session_state.messages:
        role_in_api = "model" if msg["role"] == "assistant" else "user"
        formatted_contents.append({
            "role": role_in_api,
            "parts": [{"text": msg["content"]}]
        })

    # 3. Gửi câu hỏi và hiển thị phản hồi dạng streaming
    with st.chat_message("assistant"):
        try:
            response_stream = client.models.generate_content_stream(
                model="gemini-3.8-flash",
                contents=formatted_contents,
            )

            # Đọc từng đoạn chữ trả về và hiển thị hiệu ứng gõ trực tiếp
            full_response = st.write_stream(
                chunk.text for chunk in response_stream if chunk.text
            )
            
            # Lưu lại câu trả lời vào lịch sử
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Lỗi: {e}")
