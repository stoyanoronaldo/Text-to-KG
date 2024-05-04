from rdflib import Graph, URIRef

# Create a new graph
g = Graph()

# Parse the Turtle file
try:
    g.parse("test.ttl", format="turtle")
    print("Turtle file is valid.")
except Exception as e:
    print(f"An error occurred: {e}")

# Perform additional validation checks as needed
# For example, check if a specific resource exists

'''
uri = URIRef("http://example.org/some/resource")
if (uri, None, None) in g:
    print(f"Resource {uri} exists in the graph.")
else:
    print(f"Resource {uri} not found in the graph.")

    '''