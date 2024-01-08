import streamlit as st
from streamlit_option_menu import option_menu
import fitz
from pathlib import Path
from PIL import Image
from pdf2image import convert_from_path
import pandas
import time
import shutil
import fitz
import base64
from dotenv import load_dotenv,find_dotenv
import os
from typing import List
from history_insert import insert_history
from Insert_weaviate_copy import Insert_Documents
from FInal import function_calling
import weaviate
import streamlit.components.v1 as components
from filter_bar import filter_bar
load_dotenv(find_dotenv(),override=True)
OPEN_AI_API_KEY = os.environ.get("OPEN_AI_API_KEY")
current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
samplepdf_dir = current_dir / "sample pdf"
@st.cache_data
def get_files_in_dir(path: Path) -> List[str]:
    files = []
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            files.append(file)
    return files

def show_task_bar():
    st.markdown(
        """
        <style>
            .st-emotion-cache-16txtl3 {
                padding: 1rem 0rem;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    logo = Image.open(f"assets/img/logo.png")
    st.image(logo, width=250)
    choose = option_menu(None, ["Introduction", "Config", "Chatbot"],
                         icons=['house', 'cloud-upload', 'robot'],
                         menu_icon="list", default_index=0,
                         styles={
                             "container": {"padding": "5!important", "background-color": "#f0f2f6"},
                             "icon": {"color": "#C89595", "font-size": "25px"},
                             "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px",
                                          "--hover-color": "#eee"},
                             "nav-link-selected": {"background-color": "#D9D9D9"},
                         }
                         )
    return choose

@st.cache_data
def show_ui_intro():
    image = Image.open(f"assets/img/logo.png")
    st.image(image, caption='', use_column_width=False, width=300)

    st.write("### 📝 DENSO GPT Expert - Giải pháp thông minh cho nhà máy")
    st.write(
        "DENSO GPT Expert là sản phẩm demo được phát triển bởi Đội thi SmartABI tham gia cuộc thi Factory Hacks 2023 tổ chức bởi FPTxDENSO. Sản phẩm này là một AI Chatbot với chức năng thu thập tài liệu nhà máy và hỗ trợ nhân viên nhà máy trong việc xử lý các vấn đề liên quan dựa trên tài liệu thu thập được. Đội thi SmartABI cam kết mang đến những giải pháp thông minh và sáng tạo cho ngành công nghiệp.")

    st.write("### 🤝 Member of SmartABI team:")
    "1. [Lê Đức Nguyên](https://github.com/AndrewHaward2310)"
    "2. [Trần Đức Đào Nguyên]()"
    "3. [Trần Đăng An]()"
    "4. [Lữ Xuân Đức]()"

@st.cache_data
def show_ui_config():
    st.sidebar.write("Welcome to the DENSO GPT Expert")

    # the guild of the chatbot in the sidebar
    with st.sidebar.expander("ℹ️ About"):
        st.write("Mục \"UPLOAD\" dùng để upload file PDF lên hệ thống")
        st.write("Bước 1: Click nút \"Browse files\"  để upload data lên hệ thống")
        st.write("Bước 2: Click nút \"Save to storage\" để lưu data vào hệ thống")
        st.write("Mục \"STORAGE\" dùng để xem các file PDF đã upload lên hệ thống")

    st.write('## Upload your PDF')

@st.cache_data
def image_to_base64(image):
    with open(image, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

@st.cache_data
def show_ui_chatbot():
    logo = f"assets/img/logo.png"

    # components.html(filter_bar(logo))

    st.markdown(
        """
        <div style='
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            max-width: 46rem;
            width: 100%;
            padding: 3rem;
            padding-right: 1rem;
            padding-left: 1rem;
        '>
        """,
        unsafe_allow_html=True
    )

    # Center-aligning image
    st.markdown(
        f'<div style="display: flex; justify-content: center;">'
        f'<img src="data:image/png;base64,{image_to_base64(logo)}" width="400">'
        f'</div>',
        unsafe_allow_html=True
    )

    # Center-aligning text
    st.markdown(
        '<div style="display: flex; justify-content: center; padding-left: 3rem; ">'
        '<h2>How can I help you today?</h2>'
        '</div>',
        unsafe_allow_html=True
    )
def show_pdf(file_path, page_number=1):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    pdf_show = f'<iframe src="data:application/pdf;base64,{base64_pdf}#page={page_number}" width="700" height="1000" type="application/pdf"></iframe>'

    components.html(pdf_show)
def main():
    with st.sidebar:
        choose = show_task_bar()

    if choose == "Introduction":
        show_ui_intro()

    elif choose == "Config":

        show_ui_config()
        t1, t2 = st.tabs(['UPLOAD', 'STORAGE'])

        with t1:
            uploaded_files = st.file_uploader("Choose a file", accept_multiple_files=True)

            if 'metadata_list' not in st.session_state:
                st.session_state.metadata_list = []
            file_name = [uploaded_file.name for uploaded_file in uploaded_files]
            if uploaded_files:

                for i, file in enumerate(file_name):
                    expander_title = f"File {file} Metadata"
                    if file == 'History_mayshotblash.xlsx' or file == 'History_hutbui.xlsx':
                        expander_title = f"File {file} Metadata"
                        with st.expander(expander_title):
                            form_key = f"metadata_form_{file}"
                            with st.form(form_key):
                                year = st.text_input("year", key=f"year{file}")
                                month = st.text_input("month", key=f"month{file}")
                                machine_name = st.text_input("Machine name", key=f"machine_name_{file}")
                                code = st.text_input("Code", key=f"code_{file}")
                                line = st.text_input("Line", key=f"line_{file}")
                                submit_button = st.form_submit_button("Submit")

                                if submit_button:
                                    metadata = {
                                        "source": "sample pdf/" + file,
                                        "year": year,
                                        "month": month,
                                        "machine_name": machine_name,
                                        "code": code,
                                        "line": line,
                                    }
                                    st.session_state.metadata_list.append(metadata)
                                    st.success(f"Saved metadata for {file}")
                    else:
                        with st.expander(expander_title):
                            form_key = f"metadata_form_{file}"
                            with st.form(form_key):
                                machine_name = st.text_input("Machine name", key=f"machine_name_{file}")
                                code = st.text_input("Code", key=f"code_{file}")
                                line = st.text_input("Line", key=f"line_{file}")
                                description = st.text_input("Description", key=f"description_{file}")
                                submit_button = st.form_submit_button("Submit")
                                if submit_button:
                                    metadata = {
                                        "file_path": "sample pdf/" + file,
                                        "machine_name": machine_name,
                                        "code": code,
                                        "line": line,
                                        "description": description
                                    }
                                    st.session_state.metadata_list.append(metadata)
                                    st.success(f"Saved metadata for {file}")

                result = st.button("Save to storage")
                if result:
                    with st.spinner("Processing..."):
                        st.write(st.session_state.metadata_list)

                        for metadata in st.session_state.metadata_list:
                            source = metadata.get("source", "")
                            year = metadata.get("year", "")
                            month = metadata.get("month", "")
                            machine_name = metadata.get("machine_name", "")
                            code = metadata.get("code", "")
                            line = metadata.get("line", "")

                            if source == 'sample pdf/History_mayshotblash.xlsx' or source == 'sample pdf/History_hutbui.xlsx':
                                data_dict = {
                                    "source": source,
                                    "year": year,
                                    "month": month,
                                    "machine_name": machine_name,
                                    "code": code,
                                    "line": line,
                                }
                                insert_history([data_dict])
                            else:
                                data_dict = {
                                    "file_path": metadata.get("file_path", ""),
                                    "machine_name": machine_name,
                                    "code": code,
                                    "line": line,
                                    "description": metadata.get("description", "")
                                }
                                st.write([data_dict])
                                Insert_Documents(list_documents=[data_dict])

                        if not samplepdf_dir.exists():
                            samplepdf_dir.mkdir(parents=True, exist_ok=True)

                        for uploaded_file in uploaded_files:
                            with open(os.path.join(samplepdf_dir, uploaded_file.name), "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            st.success("Saved File:{} to storage".format(uploaded_file.name))
                        st.session_state.metadata_list = []
    elif choose == "Chatbot":
        show_ui_chatbot()

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

        query = st.chat_input("🔎 Say something")
        if query:
            st.session_state.messages.append({"role": "user", "content": query})
            st.chat_message("user").write(query)
            response, metadata = function_calling(query)
            st.session_state.messages.append({"role": "bot", "content": response})
            st.chat_message("bot").write(response)


if __name__ == "__main__":
    main()