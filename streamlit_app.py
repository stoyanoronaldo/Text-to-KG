import os
from functions import *
import streamlit as st
import streamlit_agraph
from streamlit_agraph import Config, ConfigBuilder

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

if 'page_num' not in st.session_state:
    st.session_state.page_num = 1

page_options = ["Graph generation", "Graph view"]
page_selection = st.sidebar.radio(" ", page_options)

if page_selection == "Graph generation":
    st.session_state.page_num = 1
elif page_selection == "Graph view":
    st.session_state.page_num = 2

if 'answer' not in st.session_state:
    st.session_state.answer = None

if 'user_text' not in st.session_state:
    st.session_state.user_text = None

if "get_answer" not in st.session_state:
    st.session_state.get_answer = False

if "validate_turtle" not in st.session_state:
    st.session_state.validate_turtle = False

if "is_valid_turtle" not in st.session_state:
    st.session_state.is_valid_turtle = False

if st.session_state.page_num == 1:

    user_text = st.text_area(label=" ", placeholder="Enter some text", height=150, value=st.session_state.user_text or "")

    comment = """tokens = {
            'b': os.environ.get("POE_B"),
            'lat': os.environ.get("POE_LAT")
        }

    client = PoeApi(cookie=tokens)

    bot = 'llama-3-70B-T'

    
    task = '''For the given text provide all concepts and relations between them in turtle format using \
            Rdfs schema, schema.org and example.org for the enteties.\nText: '''
    question = task + user_text"""
    col1, col2= st.columns([0.15, 0.85])

    with col1:
        get_answer_btn = st.button("Get Answer")

    if get_answer_btn:
        if user_text:
            st.session_state.user_text = user_text
            st.session_state.get_answer = True
        else:
            st.write("<font color='red'>Please enter some text.</font>", unsafe_allow_html=True)
            st.session_state.get_answer = False

    with col2:
        if st.session_state.get_answer and (not st.session_state.validate_turtle):
            if st.button("Validate Turtle"):
                st.session_state.validate_turtle = True
    
    if st.session_state.validate_turtle:
        comment = """for chunk in client.send_message(bot, question):
                    pass
                save_answer_to_file(chunk["text"])
                answer = get_answer_from_string(chunk["text"])"""
        answer = get_answer_from_file('response.txt')
    
        is_valid_ttl, is_valid_string = is_valid_turtle(answer)

        if is_valid_ttl:
            st.session_state.is_valid_turtle = True
            st.write(f"<font color='green'>{is_valid_string}</font>", unsafe_allow_html=True)
            with st.expander("View turtle"):
                st.code(answer, language="turtle")
            st.session_state.answer = answer
        else:
            st.write(f"<font color='red'>{is_valid_string}</font>", unsafe_allow_html=True)

        st.session_state.validate_turtle = False
        st.session_state.get_answer = False

elif st.session_state.page_num == 2:
    if st.session_state.is_valid_turtle:
        answer = st.session_state.answer
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
    else:
        st.write("<div style='font-size: 50px; color: red;'>You don't have a valid turtle to build the graph.</div>", unsafe_allow_html=True)