from rdflib import Graph, URIRef
from streamlit_agraph import Node, Edge, TripleStore
import re
import asyncio

def get_or_create_event_loop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop

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

def save_answer_to_file(answer, file_path):
    with open(file_path, 'w') as file:
        file.write(answer)

def is_valid_turtle(ttl_string):
    g = Graph()

    try:
        g.parse(data=ttl_string, format="ttl")
        return True, "Valid Turtle"
    except Exception as e:
        return False, f"An error occurred: {e}"

def fix_turtle_syntax(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Fix common Turtle syntax issues
    # Ensure proper spacing around semicolons and periods
    #content = re.sub(r'\s*;\s*', ' ; ', content)
    #content = re.sub(r'\s*\.\s*', ' .\n', content)
    content = re.sub(r'\s*\:\s*', ':', content)

    # Ensure quotes are properly closed
    #content = re.sub(r'\"([^\"]*)\"', r'"\1"', content)

    # Write the fixed content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

    print(f"Fixed syntax in {file_path}")

def fix_turtle_syntax_string(input_string):
    # Fix common Turtle syntax issues
    # Ensure proper spacing around colons
    fixed_string = re.sub(r'\s*\:\s*', ':', input_string)

    # Ensure quotes are properly closed
    #fixed_string = re.sub(r'\"([^\"]*)\"', r'"\1"', fixed_string)

    return fixed_string

def fix_uris(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Remove line breaks within URIs
    content = re.sub(r'http://www \.\n\s*w3 \.\n\s*org/', 'http://www.w3.org/', content)
    content = re.sub(r'http://schema \.\n\s*org/', 'http://schema.org/', content)
    content = re.sub(r'http://example \.\n\s*org/', 'http://example.org/', content)

    # Write the fixed content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

    print(f"URIs fixed in {file_path}")

def fix_uris_string(input_string):
    # Remove line breaks within URIs
    fixed_string = re.sub(r'http://www \.\n\s*w3 \.\n\s*org/', 'http://www.w3.org/', input_string)
    fixed_string = re.sub(r'http://schema \.\n\s*org/', 'http://schema.org/', fixed_string)
    fixed_string = re.sub(r'http://example \.\n\s*org/', 'http://example.org/', fixed_string)

    return fixed_string

def build_graph(ttl_string):
    g = Graph()
    g.parse(data=ttl_string, format="ttl")

    made_nodes = set()

    nodes = []
    edges = []


    for subject, predicate, object in g:
        if str(subject) not in made_nodes:
            nodes.append(Node(id=str(subject), size=20, label=str(subject).split("/")[-1], title=str(subject)))
            made_nodes.add(str(subject))
        if isinstance(object, URIRef) and str(object) not in made_nodes:
            nodes.append(Node(id=str(object), size=20, label=str(object).split("/")[-1], title=str(object)))
            made_nodes.add(str(object))
        if isinstance(object, URIRef):
            edges.append(Edge(source=str(subject), target=str(object), arrowStrikethrough=False ,title=str(predicate).split("/")[-1], width=3))
        else:
            for node in nodes:
                if node.id == str(subject):
                    node.title = node.title + "\n\n" + str(predicate) + "\n" + str(object).split("/")[-1]
                    break

    return nodes, edges