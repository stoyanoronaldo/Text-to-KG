import os
import streamlit as st
from openai import OpenAI


client = OpenAI(
    api_key=os.environ.get('OPENAI_API_KEY'),
)

st.title("Text to KG")

user_text = st.text_input("Enter some text:")
question = "For the givem text provide all concepts and relations between them. \
                Present the result in turtle format using Rdfs schema, schema.org and example.org for the enteties.\nText: "

if st.button("Get Answer"):
    if user_text:
        chat_completion = client.chat.completions.create(
            messages=question + user_text,
            model="davinci-002",
            temperature=0,
            top_p=1,
            frequency_penalty=0,    
            presence_penalty=0
        )
        st.write("Answer:", chat_completion.choices[0].message.content)
    else:
        st.write("Please enter some text.")