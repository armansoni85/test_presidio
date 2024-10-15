import pandas as pd
import os
import re
from presidio_analyzer import Pattern, PatternRecognizer
from typing import List

base_path = '/usr/bin/data'  # Update this path to the actual location of the Excel file

# Load ICD-9 data from Excel file
def load_icd9_data() -> List[Pattern]:
    try:
        # Read the ICD-9 data from the Excel file
        icd9_df = pd.read_excel(os.path.join(base_path, 'ValidICD9-Jan2024.xlsx'))
        
        # Generate patterns for each ICD-9 code
        patterns = [
            Pattern(
                name=f"ICD-9 Code: {row['CODE']}",
                regex=rf"\b{re.escape(str(row['CODE']))}\b",  # Ensure the code is treated as a literal in regex
                score=0.9
            )
            for _, row in icd9_df.iterrows()
        ]
    except Exception as e:
        print(f"Error loading ICD-9 data: {e}")
        patterns = []
    return patterns

# Custom ICD-9 Recognizer
class ICD9Recognizer(PatternRecognizer):
    """Custom recognizer for ICD-9 codes and descriptions."""

    def __init__(self, supported_language: str = "en"):
        # Load ICD-9 patterns
        patterns = load_icd9_data()

        # Define the context words that may increase confidence
        context = [
            "icd-9", "code", "diagnosis", "disease", "condition", "medical"
        ]

        # Initialize the recognizer with patterns and context
        super().__init__(
            supported_entity="ICD9_CODE",
            patterns=patterns,
            context=context,
            supported_language=supported_language
        )