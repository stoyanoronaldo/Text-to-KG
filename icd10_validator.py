import xml.etree.ElementTree as ET
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# functions for creating icd10_codes.py from the icd10cm-tabular-April-2024.xml file
def load_icd10_codes():
    tree = ET.parse('icd10cm-tabular-April-2024.xml')
    root = tree.getroot()

    icd10_codes = {}

    for chapter in root.findall('.//chapter'):
        for section in chapter.findall('.//section'):
            section_desc = section.find('desc').text
            for diag in section.findall('.//diag'):
                code = diag.find('name').text
                label = diag.find('desc').text
                if label:
                    icd10_codes[label] = code

    return icd10_codes

def write_icd10_codes_to_file(icd10_codes_map):
    with open('icd10_codes.py', 'w', encoding='utf-8') as file:
        file.write("icd10_codes_map = {\n")
        for label, full_code in icd10_codes_map.items():
            file.write(f'    "{label}": "{full_code}",\n')
        file.write("}\n")
    print("The data was saved in file icd10_codes.py")

def validate_icd10_code(icd10_codes, code):
    return code in icd10_codes

# Функция за зареждане на речника от файла
def load_icd10_codes_from_file():
    from icd10_codes import icd10_codes_map
    return icd10_codes_map

icd10_codes_map = load_icd10_codes_from_file()

# Function to find the closest string
def find_closest_string_for_fhir(target_string, string_set, threshold=0.8):
    # Combine the target string with the set of strings for vectorization
    all_strings = [target_string] + list(string_set)
    
    # Vectorize the strings
    vectorizer = TfidfVectorizer().fit_transform(all_strings)
    vectors = vectorizer.toarray()
    
    # Calculate cosine similarity between the target string and the set of strings
    target_vector = vectors[0]
    set_vectors = vectors[1:]
    
    # Compute cosine similarity
    similarities = cosine_similarity([target_vector], set_vectors)[0]
    
    # Find the index of the maximum similarity
    max_similarity_index = np.argmax(similarities)
    max_similarity = similarities[max_similarity_index]
    
    # Check if the maximum similarity is above the threshold
    if max_similarity >= threshold:
        closest_label = list(string_set)[max_similarity_index]
        return closest_label, icd10_codes_map[closest_label]
    else:
        return None, None

# Function to process Turtle format
def process_turtle_format(turtle_data, icd10_codes_map):
    results = []
    
    # Split the turtle data into lines
    lines = turtle_data.strip().split('\n')
    
    for line in lines:
        if 'rdfs:label' in line:
            label = line.split('"')[1]
            closest_label, correct_code = find_closest_string_for_fhir(label, icd10_codes_map.keys())
            if correct_code:
                results.append((label, correct_code))
            else:
                results.append((label, "Code not found"))
    
    return results
