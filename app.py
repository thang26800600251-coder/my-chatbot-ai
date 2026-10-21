import time
import streamlit as st
from google import genai
from google.genai import types

# 1. Cấu hình giao diện trang web
st.set_page_config(
    page_title="Chatbot AI của Thắng",
    page_icon="⚡",
    layout="centered"
)

st.title("⚡ Chatbot AI của Thắng")
st.caption("Trợ lý AI phản hồi siêu tốc & tự động chống lỗi")

# 2. Kiểm tra API Key
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("⚠️ Chưa cấu hình GEMINI_API_KEY trong Secrets của Streamlit Cloud!")
    st.stop()

# 3. Cache kết nối Client để giữ kết nối liên tục, tăng tốc độ
@st.cache_resource
def get_client(key: str):
    return genai.Client(api_key=key)

client = get_client(api_key)

# 4. Quản lý lịch sử hội thoại
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị tin nhắn cũ
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Xử lý khi người dùng nhắn tin
if prompt := st.chat_input("Hỏi tôi bất cứ điều gì..."):
    # Hiển thị câu hỏi của người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Đóng gói 6 câu thoại gần nhất để AI xử lý nhanh
    recent_messages = st.session_state.messages[-6:]
    formatted_contents = [
        {
            "role": "model" if msg["role"] == "assistant" else "user",
            "parts": [{"text": msg["content"]}]
        }
        for msg in recent_messages
    ]

    # Danh sách các mô hình dự phòng tự động (Tùy chọn mô hình tốt nhất đang hoạt động)
    CANDIDATE_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]

    with st.chat_message("assistant"):
        full_response = ""
        success = False

        # Thử lần lượt từng mô hình nếu có lỗi
        for model_name in CANDIDATE_MODELS:
            if success:
                break

            # Tự động thử lại tối đa 3 lần nếu máy chủ Google bận
            for attempt in range(3):
                try:
                    response_stream = client.models.generate_content_stream(
                        model=model_name,
                        contents=formatted_contents,
                        config=types.GenerateContentConfig(
                            system_instruction="Bạn là trợ lý AI thông minh. Luôn trả lời ngắn gọn, trực diện, không rườm rà dài dòng.",
                            temperature=0.7,
                        )
                    )

                    # Đọc luồng chữ gõ trực tiếp
                    def stream_generator():
                        for chunk in response_stream:
                            if chunk.text:
                                yield chunk.text

                    full_response = st.write_stream(stream_generator())

                    if full_response:
                        success = True
                        break

                except Exception as e:
                    err_text = str(e)
                    # Nếu Google bị quá tải (503/429), chờ 1.5 giây rồi thử lại
                    if ("503" in err_text or "429" in err_text or "UNAVAILABLE" in err_text) and attempt < 2:
                        time.sleep(1.5)
                        continue
                    # Nếu sai tên mô hình (404/NOT_FOUND), nhảy sang mô hình tiếp theo ngay
                    elif "404" in err_text or "NOT_FOUND" in err_text:
                        break
                    else:
                        break

        # Lưu câu trả lời khi thành công
        if success and full_response:
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        elif not success:
            st.error("⚠️ Hệ thống Google AI đang bảo trì tạm thời. Bạn hãy tải lại trang (F5) sau ít phút nhé!")
