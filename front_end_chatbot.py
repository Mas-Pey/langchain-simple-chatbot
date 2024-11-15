import streamlit as st
import time
import requests
import pandas as pd

st.set_page_config(page_title="Magic Recipe", page_icon=":fork_and_knife:", layout="centered")
st.image("logo.png")
st.title(":curry: Magic Recipe :yum:")
st.write("Temukan segala Resep Makananmu")

resep_data = st.file_uploader("Upload Data")

# inisialisasi session state untuk messages, jika belum ada
if "messages" not in st.session_state:
    st.session_state.messages = []

if resep_data:
    # Spinner loading
    with st.spinner("Loading..."):
        time.sleep(1)

    # tampilkan data yang diupload
    df = pd.read_csv(resep_data)
    st.write(df)

    resep_data_str = df.to_string()

    # tampilkan pesan sebelumnya
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # menerima input user
    if prompt := st.chat_input("Ask Anything"):
        # simpan message user ke session state
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Menyusun history chat sebagai string untuk dikirim ke API
        chat_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])

        # url dan payload
        url = "http://127.0.0.1:8000/tanya-resep"
        payload = {
            "dokumen": resep_data_str,
            "text": prompt,
            "history": chat_history
        }

        # request ke API
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            # ambil response dari API
            assistant_message = response.json()
            
            # tampilkan response streaming
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message = ""
                for word in assistant_message.split():
                    message += word + " "
                    message_placeholder.markdown(message)
                    time.sleep(0.05)

                # # jika tidak streaming
                # st.markdown(assistant_message)

                # cek apakah user meminta gambar
                url = "http://127.0.0.1:8000/cek-gambar"

                response = requests.post(url, json=payload)
                if response.status_code == 200:
                    cek_gambar = response.json()
                    if cek_gambar["cek"]:
                        url_gambar = "http://127.0.0.1:8000/kirim-gambar"
                        response_gambar = requests.post(url_gambar, json=payload)
                        if response_gambar.status_code == 200:
                            kirim_gambar = response_gambar.json()
                            st.image(kirim_gambar["gambar"])

            # simpan response assitant ke session state
            st.session_state.messages.append({"role": "assistant", "content": assistant_message})
        else:
            st.error("Terjadi kesalahan saat menghubungkan API.")
