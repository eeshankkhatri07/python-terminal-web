from flask import Flask, request, render_template
from terminal import PythonTerminal  # your class file
import sys
import io
import os

app = Flask(__name__)
terminal = PythonTerminal()

# Set web context flag
import terminal as term_module
term_module.web_context = True

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run_command():
    command = request.form['command']
    
    # Capture output
    old_stdout = sys.stdout
    sys.stdout = mystdout = io.StringIO()
    
    try:
        # Process natural language input for web interface
        processed_input = terminal.process_natural_language(command)
        
        # Handle both string (single command) and tuple (command + args) cases
        if isinstance(processed_input, tuple):
            cmd, args = processed_input
        else:
            cmd = processed_input
            args = []
        
        # Split command and arguments if needed
        if not args:
            parts = cmd.split()
            if len(parts) > 1:
                cmd = parts[0]
                args = parts[1:]
            else:
                cmd = cmd
                args = []

        if cmd in terminal.commands:
            result = terminal.commands[cmd](*args)
            if result is not None:
                mystdout.write(result)
        else:
            print(f"Unknown command: {cmd}")
    except Exception as e:
        print(f"Error: {e}")
    
    sys.stdout = old_stdout
    return mystdout.getvalue()

# Add a route to handle tab completion
@app.route('/autocomplete', methods=['POST'])
def autocomplete():
    command = request.form['command']
    # Get the last word from the command
    words = command.split()
    if not words:
        return ""
    last_word = words[-1]
    
    # Get all command names
    all_commands = list(terminal.commands.keys())
    
    # Find matches
    matches = [cmd for cmd in all_commands if cmd.startswith(last_word)]
    
    # Return the first match if there's only one, or all matches
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        # Return all matches separated by space
        return " ".join(matches)
    else:
        return ""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, host='0.0.0.0', port=port)
