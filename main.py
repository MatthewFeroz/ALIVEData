import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from capture import capture_and_ocr
from summarize import summarize_text
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def main():
    Path("docs").mkdir(exist_ok=True)

    print("Taking screenshot and generating documentation...")
    ocr_result = capture_and_ocr()

    print("\nOCR Extracted Text:")
    print(ocr_result[:400], "...\n")

    summary = summarize_text(ocr_result)

    print("Generated Documentation:\n")
    print(summary)

    output_path = Path("docs") / "generated" / "generated_doc.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"\nSaved to {output_path.resolve()}")


if __name__ == "__main__":
    main()

