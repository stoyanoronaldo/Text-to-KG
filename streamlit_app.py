import os
import streamlit as st
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

st.title("Text to KG")

user_text = st.text_input("Enter some text:")
question =  question = "For the givem text provide all concepts and relations between them. \
                Present the result in turtle format using Rdfs schema, schema.org and example.org for the enteties.\nText: "                



if st.button("Get Answer"):
    if user_text:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": question + user_text,
                }
            ],
            model="gpt-3.5-turbo",
        )
        st.write("Answer:", chat_completion)
    else:
        st.write("Please enter some text.")