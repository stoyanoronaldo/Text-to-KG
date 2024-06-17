from functions import *
import streamlit as st
import streamlit_agraph
from streamlit_agraph import Config
import requests

# Ensure an event loop is created before importing llamaapi
loop = get_or_create_event_loop()

# Now you can safely import llamaapi
from llamaapi import LlamaAPI

chat_bot_is_on = True
answer = ""
api_request_json = {}
answer_content = ""
response = None

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

if "is_valid_turtle" not in st.session_state:
    st.session_state.is_valid_turtle = False

if "nodes" not in st.session_state:
    st.session_state.nodes = None

if "edges" not in st.session_state:
    st.session_state.edges = None

if st.session_state.page_num == 1:

    user_text = st.text_area(label=" ", placeholder="Enter some text", height=150, value=st.session_state.user_text or "")

    schema_options = st.radio(
        "Choose which schema to use:",
        ("schema.org", "FHIR"),
        horizontal=True
    )

    #llama = LlamaAPI(os.environ.get("LLAMA_API_KEY"))
    llama = LlamaAPI("LL-oZZ3DbV8EBPzVAdh7ylv5pQP3y0ryH77l7x50ELwEzDymcHuVOA3BnhH66HdFIZh")

    get_answer_btn = st.button("Get Answer")
    if get_answer_btn and user_text:
        st.session_state.user_text = user_text

        if chat_bot_is_on:
            if schema_options == "schema.org":
                api_request_json = {
                    "model": "llama3-70b",
                    "max_tokens": 10000,
                    "messages": [
                        {"role": "system", "content": f"For the given text provide all concepts and relations between them in turtle format. Use Rdfs schema, XML schema, schema.org. In addition for concepts use example.org."},
                        {"role": "user", "content": f"Text: {replace_non_utf8_characters(user_text)}"},
                    ]
                }
            elif schema_options == "FHIR":
                api_request_json = {
                    "model": "llama3-70b",
                    "max_tokens": 10000,
                    "messages": [
                        {"role": "system", "content": f"For the given text provide all concepts and relations between them in turtle format. Use Rdfs schema, XML schema, FHIR. In addition for concepts use example.org and mappings to icd-10."},
                        {"role": "user", "content": f"Text: {replace_non_utf8_characters(user_text)}"},
                    ]
                }

            while True:
                try:
                    response = llama.run(api_request_json)
                    response.raise_for_status()
                    answer_content = response.json()["choices"][0]["message"]["content"]
                    break
                except requests.exceptions.JSONDecodeError as e:
                    print(f"Error: {e}")
                    print()
                    print(response.text)

            if check_answer(answer_content):
                save_answer_to_file(answer_content, 'response.txt')
                answer = get_answer_from_string(answer_content)
            else:
                answer_content = fix_answer(answer_content)
                save_answer_to_file(answer_content, 'response.txt')
                answer = get_answer_from_string(answer_content)
        else:
            answer = get_answer_from_file('response.txt')

        is_valid_ttl, is_valid_string = is_valid_turtle(answer)

        if is_valid_ttl:
            st.session_state.is_valid_turtle = True
            st.write(f"<font color='green'>{is_valid_string}</font>", unsafe_allow_html=True)
            with st.expander("View turtle"):
                st.code(answer, language="turtle")
            st.session_state.answer = answer
            st.session_state.nodes = None
            st.session_state.edges = None
        else:
            st.write(f"<font color='red'>{is_valid_string}</font>", unsafe_allow_html=True)
            answer = fix_uris_string(answer)
            answer = fix_turtle_syntax_string(answer)
            save_answer_to_file(answer, 'test.ttl')
            st.write("<font color='green'>Trying to fix the error</font>", unsafe_allow_html=True)
            is_valid_ttl, is_valid_string = is_valid_turtle(answer)
            if is_valid_ttl:
                st.session_state.is_valid_turtle = True
                st.write(f"<font color='green'>{is_valid_string}</font>", unsafe_allow_html=True)
                with st.expander("View turtle"):
                    st.code(answer, language="turtle")
                st.session_state.answer = answer
                st.session_state.nodes = None
                st.session_state.edges = None
            else:
                st.write("<font color='red'>Couldn't fix it</font>", unsafe_allow_html=True)
    elif get_answer_btn and not user_text:
        st.write("<font color='red'>Please enter some text.</font>", unsafe_allow_html=True)
        
elif st.session_state.page_num == 2:
    if st.session_state.is_valid_turtle:
        answer = st.session_state.answer
        st.session_state.answer = None
        config = Config(height=550,
                    width=1200,
                    nodeHighlightBehavior=True,
                    highlightColor="#F7A7A6", 
                    directed=True,
                    physics=False, 
                    hierarchical=False, 
                    collapsible=True,
                    randomState=42)

        if st.session_state.nodes and st.session_state.edges:
            nodes = st.session_state.nodes
            edges = st.session_state.edges
        else:
            nodes, edges = build_graph(answer)
            st.session_state.nodes = nodes
            st.session_state.edges = edges

        streamlit_agraph.agraph(nodes=nodes, edges=edges, config=config)
    else:
        st.write("<div style='font-size: 50px; color: red;'>You don't have a valid turtle to build the graph.</div>", unsafe_allow_html=True)