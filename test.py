from rdflib import Graph, URIRef
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def get_answer_from_file(file_name):
    with open(file_name, 'r') as file:
        file_content = file.read()

    start_index = file_content.find("```")
    end_index = file_content.find("```", start_index + 1)
    extracted_text = file_content[start_index + 3:end_index].strip()

    return extracted_text
def extract_all_schema_org_things(graph):
    things = set()
    
    for subj, _, _ in graph:
        things.add(str(subj))
        
    return things

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
        return list(string_set)[max_similarity_index], max_similarity
    else:
        return None, max_similarity

answer = get_answer_from_file('Text-to-KG\\response.txt')
llm_graph = Graph()
llm_graph.parse(data=answer, format="ttl")

schema_graph = Graph()
schema_graph.parse("Text-to-KG\\schemaorg-all.ttl", format='ttl')
all_schema_things = extract_all_schema_org_things(schema_graph)

print(find_closest_string("http://schema.org/Award", all_schema_things))
