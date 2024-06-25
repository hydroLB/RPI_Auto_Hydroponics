import os


def clear_terminal():
    """Clears the terminal screen."""
    # Check if the operating system is Windows
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
