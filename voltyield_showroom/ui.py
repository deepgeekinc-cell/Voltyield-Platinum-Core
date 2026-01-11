import sys
import time

class ConsoleUI:
    """
    Handles all terminal output, formatting, and 'theatrical' delays.
    """
    HEADER_COLOR = "\033[92m"  # Green
    INPUT_COLOR = "\033[94m"   # Blue
    BOLD = "\033[1m"
    RESET = "\033[0m"
    WARN = "\033[93m"          # Yellow
    GRAY = "\033[90m"

    def type_writer(self, text, delay=0.01):
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        print("")

    def banner(self, version="1.2"):
        print(self.HEADER_COLOR + "="*65)
        print(f" VOLTYIELD PLATINUM | ASSET SHOWROOM v{version} (PRO) ")
        print(f" system_status: {self.BOLD}ONLINE{self.RESET}{self.HEADER_COLOR} | "
              f"secure_uplink: {self.BOLD}ACTIVE{self.RESET}")
        print(self.HEADER_COLOR + "="*65 + self.RESET)

    def get_input(self, label, default=None):
        prompt = f"   {self.INPUT_COLOR}[INPUT] {label}"
        if default:
            prompt += f" (default: {default})"
        prompt += f": {self.RESET}"

        val = input(prompt)
        return val.strip() if val.strip() else default

    def section_header(self, title):
        print(self.HEADER_COLOR + "-"*65)
        print(f"   {title}")
        print("-" * 65 + self.RESET)

    def print_kv(self, key, value, color=None):
        val_str = f"{value}"
        if color:
            val_str = f"{color}{val_str}{self.RESET}"
        print(f"      {key:<20} {val_str}")
