import os
from functions import *
import streamlit as st
import streamlit_agraph
from streamlit_agraph import Config, ConfigBuilder
from poe_api_wrapper import PoeApi


st.set_page_config(
    page_title="Text to KG",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)
def page1():

    tokens = {
            'b': 'os.environ.get("POE_B")',
            'lat': 'os.environ.get("POE_LAT")'
        }

    client = PoeApi(cookie=tokens)

    bot = 'llama-3-70B-T'

    user_text = st.text_area(label=" ", placeholder="Enter some text",height=150)
    task = """For the given text provide all concepts and relations between them in turtle format using 
            Rdfs schema, schema.org and example.org for the enteties.\nText: """
    question = task + user_text

    get_answer_buuton = st.button("Get Answer")

    if get_answer_buuton:
        if user_text:
            for chunk in client.send_message(bot, question):
                pass
            save_answer_to_file(chunk["text"])
            answer = get_answer_from_string(chunk["text"])
            st.write(answer)
            comment = """answer = get_answer_from_file('response.txt')"""
            st.code(answer, language="turtle")
        else:
            st.write("Please enter some text.")

def page2():
    answer = get_answer_from_file('response.txt')
    config = Config(height=550,
		        width=1200, 
                nodeHighlightBehavior=True,
                highlightColor="#F7A7A6", 
                directed=True,
                physics=False, 
                hierarchical=False, 
                collapsible=True)

    nodes, edges = build_graph(answer)

    streamlit_agraph.agraph(nodes=nodes, edges=edges, config=config)


page_options = ["Graph generation", "Graph view"]
page_selection = st.sidebar.radio(" ", page_options)

if page_selection == "Graph generation":
    page1()
elif page_selection == "Graph view":
    page2()