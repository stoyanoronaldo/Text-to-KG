import os
from functions import *
import streamlit as st
import streamlit_agraph
from streamlit_agraph import Config, ConfigBuilder
import asyncio

def get_or_create_event_loop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop

# Ensure an event loop is created before importing poe_api_wrapper
loop = get_or_create_event_loop()

# Now you can safely import poe_api_wrapper
from poe_api_wrapper import PoeApi


st.set_page_config(
    page_title="Text to KG",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)
def page1():

    user_text = st.text_area(label=" ", placeholder="Enter some text",height=150)

    comment = """tokens = {
            'b': os.environ.get("POE_B"),
            'lat': os.environ.get("POE_LAT")
        }

    client = PoeApi(cookie=tokens)

    bot = 'llama-3-70B-T'

    
    task = '''For the given text provide all concepts and relations between them in turtle format using \
            Rdfs schema, schema.org and example.org for the enteties.\nText: '''
    question = task + user_text"""

    get_answer_buuton = st.button("Get Answer")

    if get_answer_buuton:
        if user_text:
            comment = """for chunk in client.send_message(bot, question):
                pass
            save_answer_to_file(chunk["text"])
            answer = get_answer_from_string(chunk["text"])"""
            answer = get_answer_from_file('response.txt')
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