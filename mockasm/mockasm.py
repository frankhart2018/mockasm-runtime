import argparse

def run():
    parser = argparse.ArgumentParser(description="Mock ASM")
    parser.add_argument("--file_path", type="str", default="", help="Path to asm code")
    args = parser.parse_args()

    