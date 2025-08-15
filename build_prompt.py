import json
from langchain.prompts import ChatPromptTemplate


# Read full instruction text from file.
# This provides the general classification prompt framework for the model.
def load_instruction(file_path='prompt.txt'):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


# Load classification guidance (ontology, rules, categories) from JSON.
# This serves as the structured reference for labeling the text.
def load_guidance(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


# Build a complete classification prompt for the model.
# Combines instructions, guidance, and the target text into a ready-to-send message.
def create_prompt(segment_text, guidance_path, instruction_path='prompt.txt'):
    # Load high-level classification instructions from file
    instruction_text = load_instruction(instruction_path)

    # Load ontology/guidance from JSON file
    guidance_string = load_guidance(guidance_path)

    # Convert guidance data into JSON string format
    # Ensures human-readable Unicode characters and no extra indentation
    guidance_string = json.dumps(guidance_string, ensure_ascii=False, indent=0)

    # Create a prompt template where placeholders will be replaced with actual data
    classification_prompt = ChatPromptTemplate.from_template(
        """{instruction_text}

### Ontology Codes
{guidance_string}

### Command
Please classify the following text segment using the provided guidance:
Segment Text: "{segment_text}"
"""
    )

    # Fill placeholders in the prompt template with actual instructions, guidance, and text
    rendered_prompt = classification_prompt.format_messages(
        instruction_text=instruction_text,
        guidance_string=guidance_string,
        segment_text=segment_text
    )

    # Return the fully assembled prompt ready for use with a chat model
    return rendered_prompt
