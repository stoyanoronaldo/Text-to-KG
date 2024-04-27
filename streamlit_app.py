import os
import streamlit as st
from functions import *

openai.api_key = os.environ.get('OPENAI_API_KEY')
st.title("Text to KG")

user_text = st.text_input("Enter some text:")

if st.button("Get Answer"):
    if user_text:
        answer = generate_question_and_get_answer(user_text)
        st.write("Answer:", answer)
    else:
        st.write("Please enter some text.")