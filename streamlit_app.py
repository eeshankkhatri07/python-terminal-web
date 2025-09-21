import streamlit as st
import os
import shutil
import psutil
import sys
import io
from difflib import get_close_matches
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Set page config
st.set_page_config(
    page_title="Python Terminal Web Interface",
    page_icon="💻",
    layout="wide"
)

# Title and description
st.title("🐍 Python Terminal Web Interface")
st.markdown("""
This is a web-based terminal interface that allows you to execute system commands through your browser.
""")

# Session state for storing command history
if 'command_history' not in st.session_state:
    st.session_state.command_history = []

# Function to execute commands
def execute_command(command):
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
            mystdout.write(f"Unknown command: {cmd}")
    except Exception as e:
        mystdout.write(f"Error: {e}")
    
    sys.stdout = old_stdout
    return mystdout.getvalue()

# Function to get command suggestions
def get_suggestions(command):
    # Get all command names
    all_commands = list(terminal.commands.keys())
    
    # Find matches
    matches = [cmd for cmd in all_commands if cmd.startswith(command)]
    
    return matches

# Terminal class (reused from your original code)
class PythonTerminal:
    def __init__(self):
        self.commands = {
            "ls": self.ls,
            "pwd": self.pwd,
            "cd": self.cd,
            "mkdir": self.mkdir,
            "rm": self.rm,
            "cpu": self.cpu_usage,
            "mem": self.memory_usage,
            "df": self.disk_space,
            "ps": self.processes,
            "help": self.show_help,
            "clear": self.clear_screen
        }
        
        # Natural language command mappings
        self.natural_language_map = {
            # List commands
            "list files": "ls",
            "show files": "ls",
            "what's in this folder": "ls",
            "what's in folder": "ls",
            "show me files": "ls",
            "display files": "ls",
            
            # Directory navigation
            "change directory": "cd",
            "go to folder": "cd",
            "navigate to": "cd",
            "move to": "cd",
            "go to": "cd",
            
            # Create directory
            "make directory": "mkdir",
            "create folder": "mkdir",
            "make folder": "mkdir",
            
            # Remove
            "delete": "rm",
            "remove": "rm",
            "erase": "rm",
            "delete this": "rm",
            "remove this": "rm",
            
            # System info
            "show cpu usage": "cpu",
            "cpu usage": "cpu",
            "show memory": "mem",
            "memory usage": "mem",
            "show disk space": "df",
            "disk space": "df",
            "show processes": "ps",
            "running processes": "ps",
            
            # Utility
            "show help": "help",
            "help me": "help",
            "clear screen": "clear",
            "clear terminal": "clear"
        }
        
        # Add command aliases
        self.commands["dir"] = self.ls
        self.commands["del"] = self.rm
        
        # For Streamlit context
        self.web_context = True
        
        print("Welcome to Python Command Terminal! Type 'help' to see available commands.")

    # -----------------------------
    # File and Directory Commands
    # -----------------------------
    def ls(self, *args):
        """List files and folders in current directory"""
        try:
            # Parse options
            show_hidden = False
            show_detailed = False
            
            # Check for options
            if "-a" in args:
                show_hidden = True
            if "-l" in args:
                show_detailed = True
                
            # Get files
            files = os.listdir()
            
            # Filter out hidden files if not showing hidden
            if not show_hidden:
                files = [f for f in files if not f.startswith('.')]
                
            # Sort files (directories first)
            dirs = [f for f in files if os.path.isdir(f)]
            files = sorted(dirs) + sorted([f for f in files if not os.path.isdir(f)])
            
            if show_detailed:
                # Detailed listing
                output = ""
                for f in files:
                    file_path = os.path.join(os.getcwd(), f)
                    stat_info = os.stat(file_path)
                    
                    # Get permissions
                    permissions = oct(stat_info.st_mode)[-3:]
                    
                    # Get size
                    size = stat_info.st_size
                    
                    # Get modification time
                    import datetime
                    mod_time = datetime.datetime.fromtimestamp(stat_info.st_mtime)
                    mod_date = mod_time.strftime("%Y-%m-%d %H:%M")
                    
                    if os.path.isdir(file_path):
                        output += f"d{permissions} {size:>8} {mod_date} {f}\n"
                    else:
                        output += f"-{permissions} {size:>8} {mod_date} {f}\n"
                return output
            else:
                # Simple listing
                output = ""
                for f in files:
                    if os.path.isdir(f):
                        output += f"{f}/\n"
                    else:
                        output += f"{f}\n"
                return output
        except PermissionError:
            return f"Error: Permission denied to list directory contents"
        except OSError as e:
            return f"Error: Unable to list directory - {e}"

    def pwd(self):
        try:
            return os.getcwd()
        except OSError as e:
            return f"Error: Unable to get current directory - {e}"

    def cd(self, path):
        try:
            os.chdir(os.path.expanduser(path))
            return f"Changed directory to {os.getcwd()}"
        except FileNotFoundError:
            return "Error: Directory not found"
        except PermissionError:
            return "Error: Permission denied"
        except OSError as e:
            return f"Error: {e}"

    def mkdir(self, *names):
        """Make new directory(ies)"""
        try:
            # If no directory names are given, return error
            if not names:
                return "Error: No directory name specified"
            
            # Create all directories
            output = ""
            for name in names:
                if not name:
                    output += "Error: Directory name cannot be empty\n"
                    continue
                    
                # Support nested directories
                os.makedirs(name, exist_ok=True)
                output += f"Directory '{name}' created successfully.\n"
            return output
        except FileExistsError:
            return "Error: Directory already exists"
        except PermissionError:
            return "Error: Permission denied to create directory"
        except OSError as e:
            return f"Error: Unable to create directory - {e}"

    def rm(self, *names):
        """Remove file(s) or directory(ies)"""
        if not names:
            return "Error: No files or directories specified"
            
        output = ""
        # In web context, we can't get user input, so we'll assume confirmation
        for name in names:
            if not os.path.exists(name):
                output += f"Error: File/Directory '{name}' not found\n"
                continue
                
            try:
                if os.path.isfile(name):
                    os.remove(name)
                else:
                    shutil.rmtree(name)
                output += f"Removed '{name}' successfully.\n"
            except PermissionError:
                output += f"Error: Permission denied to remove '{name}'\n"
            except OSError as e:
                output += f"Error: Unable to remove '{name}' - {e}\n"
        return output

    # -----------------------------
    # System Monitoring Commands
    # -----------------------------
    def cpu_usage(self):
        return f"CPU Usage: {psutil.cpu_percent()}%"

    def memory_usage(self):
        mem = psutil.virtual_memory()
        return f"Memory Usage: {mem.percent}%"

    def disk_space(self):
        disk = psutil.disk_usage('/')
        output = f"Disk Total: {disk.total / (1024**3):.2f} GB\n"
        output += f"Disk Used: {disk.used / (1024**3):.2f} GB\n"
        output += f"Disk Free: {disk.free / (1024**3):.2f} GB\n"
        return output

    def processes(self):
        output = ""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                output += f"PID: {proc.info['pid']}, Name: {proc.info['name']}\n"
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return output

    # -----------------------------
    # Utility Commands
    # -----------------------------
    def show_help(self, *args):
        help_text = [
            ("ls", "List files and folders in current directory"),
            ("pwd", "Print current working directory"),
            ("cd <path>", "Change directory"),
            ("mkdir <name>", "Make new directory (supports multiple dirs)"),
            ("rm <name>", "Remove file or directory (supports multiple items)"),
            ("cpu", "Show CPU usage"),
            ("mem", "Show memory usage"),
            ("df", "Show disk space"),
            ("ps", "Show running processes"),
            ("dir", "Alias for ls - list files"),
            ("del", "Alias for rm - delete files"),
            ("help", "Display this help message"),
            ("clear", "Clear the terminal screen"),
            ("exit", "Exit the terminal")
        ]
        
        output = "Available Commands:\n"
        for cmd, desc in help_text:
            output += f"{cmd:15} - {desc}\n"
        return output

    def clear_screen(self):
        # For Streamlit, we can't actually clear the terminal, but we can reset the session state
        return "Screen cleared"

    # -----------------------------
    # Natural Language Processing
    # -----------------------------
    def process_natural_language(self, user_input):
        """Convert natural language input to standard command format"""
        # Convert to lowercase for easier matching
        lower_input = user_input.lower().strip()
        
        # Check for exact matches in our natural language map
        if lower_input in self.natural_language_map:
            return self.natural_language_map[lower_input]
        
        # Check for partial matches (for commands with arguments)
        for nl_cmd, standard_cmd in self.natural_language_map.items():
            if lower_input.startswith(nl_cmd + " ") or lower_input == nl_cmd:
                # Return the standard command and the rest of the input as arguments
                if lower_input == nl_cmd:
                    return standard_cmd, []
                else:
                    # Extract arguments after the natural language command
                    args = user_input[len(nl_cmd):].strip()
                    return standard_cmd, [args] if args else []
        
        # If no natural language match, return original input
        return user_input

# Initialize terminal
terminal = PythonTerminal()

# Sidebar for navigation
with st.sidebar:
    st.header("Navigation")
    st.markdown("---")
    st.subheader("Commands")
    st.markdown("- ls: List files")
    st.markdown("- pwd: Show current directory")
    st.markdown("- cd: Change directory")
    st.markdown("- mkdir: Create directory")
    st.markdown("- rm: Remove files/dirs")
    st.markdown("- cpu/mem/df: System info")
    st.markdown("- ps: Processes")
    st.markdown("- help: Show help")
    st.markdown("---")
    st.subheader("About")
    st.markdown("Python Terminal Web Interface")
    st.markdown("Built with Streamlit")

# Main content area
st.subheader("Terminal Interface")

# Command input
command = st.text_input("Enter command:", key="command_input")

# Execute button
if st.button("Execute"):
    if command.strip():
        # Add to command history
        st.session_state.command_history.append(f"> {command}")
        
        # Execute command
        result = execute_command(command)
        
        # Add result to history
        st.session_state.command_history.append(result)
        
        # Clear the input field
        st.experimental_rerun()

# Display command history
if st.session_state.command_history:
    st.subheader("Command History")
    history_text = "\n".join(st.session_state.command_history)
    st.code(history_text, language="bash")

# Add a clear history button
if st.button("Clear History"):
    st.session_state.command_history = []
    st.experimental_rerun()

# Footer
st.markdown("---")
st.caption("⚠️ Warning: This interface allows execution of system commands. Use responsibly.")
