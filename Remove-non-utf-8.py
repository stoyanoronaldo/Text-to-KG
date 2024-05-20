import unicodedata

def replace_non_utf8_characters(text):
    # Normalize the text to a standard form, 'NFC' composes decomposed characters
    normalized_text = unicodedata.normalize('NFC', text)
    
    # Encode to UTF-8, then decode back to string, ignoring errors
    utf8_text = normalized_text.encode('utf-8', 'ignore').decode('utf-8')
    
    # Return the cleaned text
    return utf8_text

# Example usage:
original_text = "Add text here"
clean_text = replace_non_utf8_characters(original_text)
print(clean_text)