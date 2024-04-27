import os
import streamlit as st
from functions import *


st.title("Text to KG")

user_text = st.text_input("Enter some text:")
question =  question = "For the givem text provide all concepts and relations between them. \
                Present the result in turtle format using Rdfs schema, schema.org and example.org for the enteties.\nText: "                

if st.button("Get Answer"):
    if user_text:
        answer = chat_with_chatgpt(question + user_text)
        st.write("Answer:", answer)
    else:
        st.write("Please enter some text.")