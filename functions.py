from rdflib import Graph, URIRef, BNode
from streamlit_agraph import Node, Edge
import re
import unicodedata

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

def check_answer(str):
    start_index = str.find("```")
    end_index = str.find("```", start_index + 1)
    if start_index != -1 and end_index != -1:
        return True
    return False

def fix_answer(str):
    fixed_string = ""
    start_index = str.find("```")
    if start_index == -1:
        fixed_string = str + "\n``` ```\n"
    end_index = str.find("```", start_index + 1)
    if end_index == -1:
        fixed_string = str + "\n```"
    return fixed_string
    

def is_valid_turtle(ttl_string):
    g = Graph()

    try:
        g.parse(data=ttl_string, format="ttl")
        return True, "Valid Turtle"
    except Exception as e:
        return False, f"An error occurred: {e}"

def text_has_xsd(text):
    return "xsd" in text

def text_has_xsd_prefix(text):
    return "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> ." in text

def add_xsd_prefix(text):
    text = "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> ." + "\n" + text
    return text

def fix_turtle_syntax_string(input_string):
    # Fix common Turtle syntax issues
    # Ensure proper spacing around colons
    fixed_string = re.sub(r'\s*\:\s*', ':', input_string)

    fixed_string = re.sub(r'(example:[^\s]+)\s([^\s]+) (a schema:)', r'\1_\2 \3', fixed_string, flags=re.MULTILINE)

    if text_has_xsd(fixed_string) and (not(text_has_xsd_prefix(fixed_string))):
        fixed_string = add_xsd_prefix(fixed_string)
    
    # Ensure quotes are properly closed
    #fixed_string = re.sub(r'\"([^\"]*)\"', r'"\1"', fixed_string)

    return fixed_string

def fix_uris_string(input_string):
    # Remove line breaks within URIs
    fixed_string = re.sub(r'http://www \.\n\s*w3 \.\n\s*org/', 'http://www.w3.org/', input_string)
    fixed_string = re.sub(r'http://schema \.\n\s*org/', 'http://schema.org/', fixed_string)
    fixed_string = re.sub(r'http://example \.\n\s*org/', 'http://example.org/', fixed_string)

    return fixed_string

def replace_non_utf8_characters(text):
    # Normalize the text to a standard form, 'NFC' composes decomposed characters
    normalized_text = unicodedata.normalize('NFC', text)
    
    # Encode to UTF-8, then decode back to string, ignoring errors
    utf8_text = normalized_text.encode('utf-8', 'ignore').decode('utf-8')
    
    # Return the cleaned text
    return utf8_text

def build_graph(ttl_string):
    g = Graph()
    g.parse(data=ttl_string, format="ttl")

    made_nodes = set()

    nodes = []
    edges = []


    for subject, predicate, object in g:
        if not isinstance(subject, BNode) and not isinstance(object, BNode):
            if str(subject) not in made_nodes:
                nodes.append(Node(id=str(subject), size=20, label=str(subject).split("/")[-1], title=str(subject)))
                made_nodes.add(str(subject))
            if isinstance(object, URIRef) and str(object) not in made_nodes:
                nodes.append(Node(id=str(object), size=20, label=str(object).split("/")[-1], title=str(object)))
                made_nodes.add(str(object))
            if isinstance(object, URIRef):
                edges.append(Edge(source=str(subject), target=str(object), arrowStrikethrough=False ,label=str(predicate).split("/")[-1].split("#")[-1], width=3))
            else:
                for node in nodes:
                    if node.id == str(subject):
                        node.title = node.title + "\n\n" + str(predicate) + "\n" + str(object).split("/")[-1]
                        break

    return nodes, edges