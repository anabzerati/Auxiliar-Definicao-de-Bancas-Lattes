import argparse
import warnings

def main():
    theme: str = input("Enter the title of your theme: ")

    summary_file = input("Enter the path to the summary file (leave empty to skip): ").strip()

    if summary_file:
        try:
            with open(summary_file, "r", encoding="utf-8") as file:
                resumo = file.read()
        except FileNotFoundError:
            raise FileNotFoundError("The specified file does not exist.")
    else:
        warnings.warn("No summary file provided. Only the title will be used to find the TCC committee.", UserWarning)

    print("\n=== Input Summary ===")
    print(f"Title: {theme}")
    if summary_file:
        print(f"Summary file: {summary_file}")
    else:
        print("Summary file: (none provided)")

if __name__ == "__main__":
    main()
