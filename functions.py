from rdflib import Graph, URIRef, BNode
from streamlit_agraph import Node, Edge
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
import unicodedata
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

def extract_all_schema_org_classes(graph):
    clases = set()
    
    for subj, _, obj in graph:
        if str(obj) == "http://www.w3.org/2000/01/rdf-schema#Class":
            clases.add(str(subj))
        
    return clases

def extract_all_schema_org_properties(graph):
    properties = set()
    
    for subj, _, obj in graph:
        if str(obj) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#Property":
            properties.add(str(subj))
        
    return properties

def find_closest_string(target_string, string_set, threshold=0.8):
    # Combine the target string with the set of strings for vectorization
    all_strings = [target_string] + list(string_set)
    
    # Vectorize the strings
    vectorizer = TfidfVectorizer().fit_transform(all_strings)
    vectors = vectorizer.toarray()
    
    # Compute cosine similarity between the target string and the set of strings
    target_vector = vectors[0]
    set_vectors = vectors[1:]
    
    # Calculate cosine similarities
    similarities = cosine_similarity([target_vector], set_vectors)[0]
    
    # Find the index of the maximum similarity
    max_similarity_index = np.argmax(similarities)
    max_similarity = similarities[max_similarity_index]
    
    # Check if the maximum similarity is above the threshold
    if max_similarity >= threshold:
        return list(string_set)[max_similarity_index]
    else:
        return None

def build_graph(ttl_string):
    llm_graph = Graph()
    llm_graph.parse(data=ttl_string, format="ttl")

    schema_graph = Graph()
    schema_graph.parse('schemaorg-all.ttl', format='ttl')
    all_schema_classes = extract_all_schema_org_classes(schema_graph)
    all_schema_properties = extract_all_schema_org_properties(schema_graph)

    made_nodes = set()

    nodes = []
    edges = []

    for subject, predicate, object in llm_graph:
        if not isinstance(subject, BNode) and not isinstance(object, BNode):
            if str(subject) not in made_nodes:
                nodes.append(Node(id=str(subject), size=20, label=str(subject).split("/")[-1], title=str(subject)))
                made_nodes.add(str(subject))
            if isinstance(object, URIRef) and str(object) not in made_nodes:
                if('schema.org' in str(object)):
                    closest_string = find_closest_string(str(object), all_schema_classes)
                    if closest_string:
                        object = URIRef(closest_string)
                        nodes.append(Node(id=closest_string, size=20, label=closest_string.split("/")[-1], title=closest_string))
                        made_nodes.add(str(object))
                    else:
                        continue
                else:
                    nodes.append(Node(id=str(object), size=20, label=str(object).split("/")[-1], title=str(object)))
                    made_nodes.add(str(object))
            if isinstance(object, URIRef):
                if('schema.org' in str(predicate)):
                    closest_string = find_closest_string(str(predicate), all_schema_properties)
                    if closest_string:
                        edges.append(Edge(source=str(subject), target=str(object), arrowStrikethrough=False ,label=closest_string.split("/")[-1].split("#")[-1], width=3))
                else:
                    edges.append(Edge(source=str(subject), target=str(object), arrowStrikethrough=False ,label=str(predicate).split("/")[-1].split("#")[-1], width=3))
            else:
                if('schema.org' in str(predicate)):
                    closest_string = find_closest_string(str(predicate), all_schema_properties)
                    if closest_string:
                        for node in nodes:
                            if node.id == str(subject):
                                node.title = node.title + "\n\n" + str(predicate) + "\n" + str(object).split("/")[-1]
                                break
                else:
                    for node in nodes:
                        if node.id == str(subject):
                            node.title = node.title + "\n\n" + str(predicate) + "\n" + str(object).split("/")[-1]
                            break

    return nodes, edges