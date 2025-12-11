import re
from typing import Dict, Optional

# This list should match your model's choices for validation
LEAD_CLASSIFICATIONS = [
    'New', 'Contacted', 'Growing Interest', 'Leading',
    'Dying', 'Converted', 'Cold'
]

def extract_lead_data(text: str) -> Dict[str, Optional[str]]:
    """
    Extracts structured lead information from raw LLM text using regex.
    Returns a dictionary where keys match the Django model field names.
    """
    
    # --- Define Hardcoded Patterns ---
    # Note: These patterns are based on common LLM outputs like "Email: user@example.com"
    # You MUST adjust them to match the format your LLM actually produces.
    
    patterns = {
        'full_name': r'(?:Name|Full Name|Contact):\s*(.+?)(?=\n|$)',
        'company': r'(?:Company|Organization):\s*(.+?)(?=\n|$)',
        'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        'phone_number': r'(?:Phone|Tel):\s*(\+?\d{1,4}[\s-]?\(?\d{1,4}\)?[\s-]?\d{1,4}[\s-]?\d{1,9})',
        'website': r'(?:Website|URL|Site):\s*(https?://[^\s]+)',
        'address': r'(?:Address|Location):\s*(.+?)(?=\n|$)',
    }
    
    # Dynamically create a pattern for lead classification to be extra safe
    # This will only match one of the predefined choices.
    class_choices = '|'.join(re.escape(choice) for choice in LEAD_CLASSIFICATIONS)
    patterns['lead_class'] = rf'(?:Status|Classification|Lead Class):\s*({class_choices})'
    
    extracted_data = {}
    
    # --- Apply Patterns ---
    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # For patterns with a capture group (like Name: ...), use the group.
            # For patterns without a capture group (like the raw email), use the whole match.
            extracted_data[field] = match.group(1) if match.lastindex else match.group(0)
        else:
            extracted_data[field] = None

    # Clean up whitespace
    for key, value in extracted_data.items():
        if isinstance(value, str):
            extracted_data[key] = value.strip()

    return extracted_data
