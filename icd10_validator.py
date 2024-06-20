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
def find_closest_string_for_fhir(target_string, string_set, threshold=0.7):
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
            if closest_label:
                results.append((label, closest_label, correct_code))
            else:
                results.append((label, "Closest label not found", "Code not found"))
    
    return results

def update_and_clean_turtle(turtle_data, results):
    lines = turtle_data.strip().split('\n')
    cleaned_lines = []
    inside_block = False
    current_block = []
    block_label = ""
    new_icd10_code = None
    old_icd10_code = None
    is_code_present = False

    for line in lines:
        stripped_line = line.strip()

        # Check if we are entering a new block
        if stripped_line.startswith('example:') and not stripped_line.endswith('.'):
            if inside_block:
                # Finish the current block
                if new_icd10_code:
                    current_block.insert(2, new_icd10_code)  # Insert after type definition
                elif old_icd10_code:
                    current_block.insert(2, old_icd10_code)  # Insert after type definition
                cleaned_lines.extend(current_block)
                current_block = [line]
                block_label = ""
                new_icd10_code = None
                old_icd10_code = None
                is_code_present = False
            else:
                inside_block = True
                current_block = [line]
        elif inside_block:
            # Check if the line contains an ICD-10 code
            if 'icd10:code' in stripped_line:
                is_code_present = True
                if not old_icd10_code:
                    old_icd10_code = line
                continue
            if 'fhir:code' in stripped_line:
                # Extract the old ICD-10 code and ignore the line
                old_code_match = re.search(r'fhir:code \[ fhir:system "http://hl7.org/fhir/sid/icd-10-cm" ; fhir:code "([^"]+)" \]', stripped_line)
                if old_code_match:
                    old_icd10_code = f'  icd10:code "{old_code_match.group(1)}" ;'
                continue
            if 'rdfs:label' in stripped_line:
                block_label = stripped_line.split('"')[1]
                # Check if there's a new ICD-10 code for this label
                for result in results:
                    if result[0] == block_label and result[2] != "Code not found":
                        new_icd10_code = f'  icd10:code "{result[2]}" ;'
                        is_code_present = True
                        break
            current_block.append(line)
            if stripped_line.endswith('.'):
                if new_icd10_code:
                    current_block.insert(2, new_icd10_code)  # Insert after type definition
                elif old_icd10_code and not is_code_present:
                    current_block.insert(2, old_icd10_code)  # Insert after type definition
                inside_block = False
                cleaned_lines.extend(current_block)
                current_block = []
                block_label = ""
                new_icd10_code = None
                old_icd10_code = None
                is_code_present = False
        else:
            cleaned_lines.append(line)

    # Handle the last block if still open
    if inside_block:
        if new_icd10_code:
            current_block.insert(2, new_icd10_code)  # Insert after type definition
        elif old_icd10_code and not is_code_present:
            current_block.insert(2, old_icd10_code)  # Insert after type definition
        cleaned_lines.extend(current_block)

    # Remove any extra dots at the end of the line
    final_lines = []
    for line in cleaned_lines:
        if line.strip().endswith(' ; .'):
            final_lines.append(line.replace(' ; .', ' ;'))
        elif line.strip().endswith('. .'):
            final_lines.append(line.replace('. .', ' .'))
        else:
            final_lines.append(line)

    return "\n".join(final_lines)

def fix_turtle_format(text):
    # Split the text into blocks
    blocks = text.split('\n\n')

    # Modify the other lines (except the first one) to end with a semicolon
    for i in range(len(blocks)):
        if i > 0:
            lines = blocks[i].split('\n')
            for j in range(1, len(lines)):
                if lines[j].strip().endswith('.'):
                    lines[j] = lines[j].rstrip('.') + ';'
            blocks[i] = '\n'.join(lines)
    
    # Modify the last line in each block if it ends with a semicolon
    for i in range(len(blocks)):
        lines = blocks[i].split('\n')
        if lines[-1].strip().endswith(';'):
            lines[-1] = lines[-1].rstrip(';') + '.'
        blocks[i] = '\n'.join(lines)
    
    # Join the blocks back into text
    fixed_text = '\n\n'.join(blocks)
    return fixed_text