import os
import shutil
import psutil
import readline  # For command history and auto-completion
from difflib import get_close_matches
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Flag to track if we're in web context (to disable colors)
web_context = False

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
        
        self.setup_readline()
        if not web_context:
            print(Fore.GREEN + "Welcome to Python Command Terminal! Type 'help' to see available commands.")
        else:
            print("Welcome to Python Command Terminal! Type 'help' to see available commands.")

    # -----------------------------
    # Readline Setup for History & Autocomplete
    # -----------------------------
    def setup_readline(self):
        readline.parse_and_bind("tab: complete")
        readline.set_completer(self.complete)

    def complete(self, text, state):
        options = [cmd for cmd in self.commands if cmd.startswith(text)]
        if state < len(options):
            return options[state]
        else:
            return None

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
                        if web_context:
                            print(f"d{permissions} {size:>8} {mod_date} {f}")
                        else:
                            print(Fore.BLUE + f"d{permissions} {size:>8} {mod_date} {f}")
                    else:
                        if web_context:
                            print(f"-{permissions} {size:>8} {mod_date} {f}")
                        else:
                            print(f"-{permissions} {size:>8} {mod_date} {f}")
            else:
                # Simple listing
                for f in files:
                    if os.path.isdir(f):
                        if web_context:
                            print(f)
                        else:
                            print(Fore.BLUE + f)
                    else:
                        if web_context:
                            print(f)
                        else:
                            print(f)
        except PermissionError:
            print(Fore.RED + "Error: Permission denied to list directory contents")
        except OSError as e:
            print(Fore.RED + f"Error: Unable to list directory - {e}")

    def pwd(self):
        try:
            if web_context:
                print(os.getcwd())
            else:
                print(Fore.GREEN + os.getcwd())
        except OSError as e:
            print(Fore.RED + f"Error: Unable to get current directory - {e}")

    def cd(self, path):
        try:
            os.chdir(os.path.expanduser(path))
        except FileNotFoundError:
            print(Fore.RED + "Error: Directory not found")
        except PermissionError:
            print(Fore.RED + "Error: Permission denied")
        except OSError as e:
            print(Fore.RED + f"Error: {e}")

    def mkdir(self, *names):
        """Make new directory(ies)"""
        try:
            # If no directory names are given, prompt the user
            if not names:
                name = input("Enter new directory name: ").strip()
                if not name:
                    print(Fore.RED + "Error: Directory name cannot be empty")
                    return
                names = [name]
            
            # Create all directories
            for name in names:
                if not name:
                    print(Fore.RED + "Error: Directory name cannot be empty")
                    continue
                    
                # Support nested directories
                os.makedirs(name, exist_ok=True)
                if web_context:
                    print(f"Directory '{name}' created successfully.")
                else:
                    print(Fore.GREEN + f"Directory '{name}' created successfully.")
        except FileExistsError:
            print(Fore.RED + "Error: Directory already exists")
        except PermissionError:
            print(Fore.RED + "Error: Permission denied to create directory")
        except OSError as e:
            print(Fore.RED + f"Error: Unable to create directory - {e}")


    def rm(self, *names):
        """Remove file(s) or directory(ies)"""
        if not names:
            print(Fore.RED + "Error: No files or directories specified")
            return
            
        # In web context, we can't get user input, so we'll assume confirmation
        # For production use, you'd want to implement a proper confirmation mechanism
        for name in names:
            if not os.path.exists(name):
                print(Fore.RED + f"Error: File/Directory '{name}' not found")
                continue
                
            # Skip confirmation in web context
            if web_context:
                print(f"Removing '{name}' (web context - no confirmation)")
            else:
                confirm = input(f"Are you sure you want to remove '{name}'? (y/N): ")
                if confirm.lower() not in ["y", "yes"]:
                    print(f"Operation cancelled for '{name}'.")
                    continue
                    
            try:
                if os.path.isfile(name):
                    os.remove(name)
                else:
                    shutil.rmtree(name)
                if web_context:
                    print(f"Removed '{name}' successfully.")
                else:
                    print(Fore.GREEN + f"Removed '{name}' successfully.")
            except PermissionError:
                print(Fore.RED + f"Error: Permission denied to remove '{name}'")
            except OSError as e:
                print(Fore.RED + f"Error: Unable to remove '{name}' - {e}")

    # -----------------------------
    # System Monitoring Commands
    # -----------------------------
    def cpu_usage(self):
        print(f"CPU Usage: {psutil.cpu_percent()}%")

    def memory_usage(self):
        mem = psutil.virtual_memory()
        print(f"Memory Usage: {mem.percent}%")

    def disk_space(self):
        disk = psutil.disk_usage('/')
        print(f"Disk Total: {disk.total / (1024**3):.2f} GB")
        print(f"Disk Used: {disk.used / (1024**3):.2f} GB")
        print(f"Disk Free: {disk.free / (1024**3):.2f} GB")

    def processes(self):
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                print(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

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
        
        output = "\nAvailable Commands:\n"
        for cmd, desc in help_text:
            output += f"{cmd:15} - {desc}\n"
        return output

    def clear_screen(self):
        # In web context, we can't clear the terminal screen directly
        # So we'll just print a newline character to simulate clearing
        if web_context:
            print("\n" * 100)  # Print many newlines to simulate clearing
        else:
            os.system('cls' if os.name == 'nt' else 'clear')

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

    # -----------------------------
    # Main Loop
    # -----------------------------
    def run(self):
        # Get username
        import getpass
        username = getpass.getuser()
        
        while True:
            try:
                prompt = Fore.CYAN + f"{username}@PythonTerminal:{os.getcwd()}$ " + Style.RESET_ALL
                user_input = input(prompt).strip()
                if not user_input:
                    continue
                
                # Process natural language input
                processed_input = self.process_natural_language(user_input)
                
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

                if cmd == "exit":
                    if web_context:
                        print("Goodbye!")
                    else:
                        print(Fore.GREEN + "Goodbye!")
                    break

                if cmd in self.commands:
                    func = self.commands[cmd]
                    func(*args) if args else func()
                else:
                    suggestion = get_close_matches(cmd, self.commands.keys())
                    if suggestion:
                        if web_context:
                            print(f"Unknown command '{cmd}'. Did you mean: {', '.join(suggestion)}?")
                        else:
                            print(Fore.RED + f"Unknown command '{cmd}'. Did you mean: {', '.join(suggestion)}?")
                    else:
                        if web_context:
                            print(f"Unknown command '{cmd}'. Type 'help' for available commands.")
                        else:
                            print(Fore.RED + f"Unknown command '{cmd}'. Type 'help' for available commands.")

            except KeyboardInterrupt:
                if web_context:
                    print("\nExiting...")
                else:
                    print("\n" + Fore.GREEN + "Exiting...")
                break
            except EOFError:
                if web_context:
                    print("\nExiting...")
                else:
                    print("\n" + Fore.GREEN + "Exiting...")
                break
            except TypeError:
                if web_context:
                    print("Error: Invalid arguments for command")
                else:
                    print(Fore.RED + "Error: Invalid arguments for command")
            except Exception as e:
                if web_context:
                    print(f"Unexpected error: {e}")
                else:
                    print(Fore.RED + f"Unexpected error: {e}")

if __name__ == "__main__":
    terminal = PythonTerminal()
    terminal.run()
