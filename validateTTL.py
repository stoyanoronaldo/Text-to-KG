from rdflib import Graph, URIRef
import re

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

# Usage
#fix_uris('test.ttl')

is_ok = True
# Create a new graph
g = Graph()

# Parse the Turtle file
try:
    g.parse("test.ttl", format="turtle")
    print("Turtle file is valid.")
except Exception as e:
    print(f"An error occurred: {e}")
    is_ok = False

# Perform additional validation checks as needed
# For example, check if a specific resource exists

'''
uri = URIRef("http://example.org/some/resource")
if (uri, None, None) in g:
    print(f"Resource {uri} exists in the graph.")
else:
    print(f"Resource {uri} not found in the graph.")

    '''

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

# Usage
if(not is_ok):
  fix_turtle_syntax('test.ttl')
