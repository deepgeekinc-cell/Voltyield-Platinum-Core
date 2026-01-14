import sys, time

class ConsoleUI:
    HEADER = "\033[92m"
    INPUT = "\033[94m"
    RESET = "\033[0m"

    def type_writer(self, text):
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(0.01)
        print("")

    def banner(self):
        print(f"{self.HEADER}" + "="*60)
        print(" VOLTYIELD PLATINUM | ASSET SHOWROOM v1.2")
        print("="*60 + f"{self.RESET}")

    def get_input(self, label, default):
        val = input(f"   {self.INPUT}[INPUT] {label} (default: {default}): {self.RESET}")
        return val.strip() if val.strip() else default

    def print_kv(self, key, value):
        print(f"      {key:<20} {value}")
