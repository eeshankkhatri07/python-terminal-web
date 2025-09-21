# Python Terminal Web Interface

A web-based terminal interface that allows users to execute system commands through a browser.

## Features

- Web-based terminal interface
- Execute common system commands (ls, cd, mkdir, rm, etc.)
- System monitoring commands (cpu, mem, df, ps)
- Natural language command processing
- Tab completion and command history

## Requirements

- Python 3.6+
- Flask
- psutil
- colorama

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python app.py
```

Then open your browser and go to `http://localhost:5001`

## Deployment

This application can be deployed to various cloud platforms like Heroku, Render, etc.

## Available Commands

- `ls` - List files and folders
- `pwd` - Print current working directory
- `cd <path>` - Change directory
- `mkdir <name>` - Make new directory
- `rm <name>` - Remove file or directory
- `cpu` - Show CPU usage
- `mem` - Show memory usage
- `df` - Show disk space
- `ps` - Show running processes
- `help` - Display help message
- `clear` - Clear the terminal screen
