from rdflib import Graph
from streamlit_agraph import Node, Edge, TripleStore

def get_answer_from_file(file_name):
    with open(file_name, 'r') as file:
        file_content = file.read()

    start_index = file_content.find("```")
    end_index = file_content.find("```", start_index + 1)
    extracted_text = file_content[start_index + 3:end_index].strip()

    return extracted_text

def get_answer_from_string(str):
    start_index = str.find("```")
    end_index = str.find("```", start_index + 1)
    extracted_text = str[start_index + 3:end_index].strip()

    return extracted_text

def save_answer_to_file(answer):
    file_path = 'response.txt'

    with open(file_path, 'w') as file:
        file.write(answer)

def build_graph(ttl_string):
    g = Graph()
    g.parse(data=ttl_string, format="ttl")

    made_nodes = set()

    nodes = []
    edges = []


    for s, p, o in g:
        if str(s) not in made_nodes:
            nodes.append(Node(id=str(s), size=20, title=str(s)))
            made_nodes.add(str(s))
        if str(o) not in made_nodes:
            nodes.append(Node(id=str(o), size=20, title=str(o)))
            made_nodes.add(str(o))
        edges.append(Edge(source=str(s), target=str(o), type="CURVE_SMOOTH", title=str(p), width=3))

    return nodes, edges