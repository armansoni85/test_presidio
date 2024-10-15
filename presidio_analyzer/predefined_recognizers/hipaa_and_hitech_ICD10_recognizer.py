import pandas as pd
import re
import os
from presidio_analyzer import Pattern, PatternRecognizer
from typing import List

base_path = '/usr/bin/data'

def load_icd10_data() -> List[Pattern]:
    """Load ICD-10 data from the Excel file and create regex patterns."""
    patterns = []
    try:
        icd10_df = pd.read_excel(os.path.join(base_path, 'ValidICD10-Jan2024.xlsx'))
        
        for _, row in icd10_df.iterrows():
            code = row['CODE']
            short_desc = row['SHORT DESCRIPTION (VALID ICD-10 FY2024)']
            long_desc = row['LONG DESCRIPTION (VALID ICD-10 FY2024)']
            
            # Add patterns for each type of description
            patterns.append(Pattern(f"ICD-10 Code: {code}", rf"\b{code}\b", 1.0))
            patterns.append(Pattern(f"ICD-10 Short Desc: {short_desc}", re.escape(short_desc), 0.7))
            patterns.append(Pattern(f"ICD-10 Long Desc: {long_desc}", re.escape(long_desc), 0.7))
    
    except Exception as e:
        print(f"Error loading ICD-10 data: {e}")
    
    return patterns

class ICD10Recognizer(PatternRecognizer):
    """Recognizer for identifying ICD-10 codes and descriptions."""
    
    def __init__(
        self,
        supported_language: str = "en",
        supported_entity: str = "ICD10_CODE",
    ):
        # Load patterns
        patterns = load_icd10_data()
        
        context = ["icd-10", "code", "diagnosis", "disease", "condition", "medical"]
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

