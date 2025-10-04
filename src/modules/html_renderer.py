import os
import re

def render(interpreter, template_path, context):
    """
    Renders an HTML template by replacing placeholders with values from a context map.
    - interpreter: The Mrya interpreter instance, used to resolve paths.
    - template_path: The path to the HTML file, relative to the calling Mrya script.
    - context: A dictionary of variables to inject into the template.
    """
    # Resolve the template path relative to the Mrya script's directory
    full_path = os.path.abspath(os.path.join(interpreter.current_directory, template_path))

    if not os.path.exists(full_path):
        raise RuntimeError(f"HTML template not found at '{full_path}'")

    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # This is the replacement function for re.sub. It looks up the variable in the context.
    def replace_var(match):
        var_name = match.group(1)
        # Get the value from the context, default to a warning message if not found.
        return str(context.get(var_name, f"[$ UNDEFINED: {var_name} $]"))

    # The regex pattern for finding placeholders like [$ variable_name $]
    pattern = r'\[\$\s*(\w+)\s*\$\]'
    rendered_content = re.sub(pattern, replace_var, content)
    
    return rendered_content