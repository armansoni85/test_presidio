from typing import List, Optional
from presidio_analyzer import Pattern, PatternRecognizer
import pandas as pd
import re
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

class LowThresholdHIPAARecognizer(PatternRecognizer):
    """
    Recognize entities that are associated with low-threshold HIPAA violations.
    Includes detection of unformatted SSNs, specific US date formats, and ICD-9/ICD-10 codes.
    """

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "LOW_THRESHOLD_HIPAA",
    ):
        if patterns is None:
            patterns = self._load_patterns()
        if context is None:
            context = self._load_context()
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    @staticmethod
    def _load_patterns() -> List[Pattern]:
        """
        Load all patterns, including SSNs, US date formats, and ICD-9/ICD-10 codes.
        Patterns for ICD codes are loaded lazily from their respective data files using parallel processing.
        """
        # Pattern 1: 6-digit or greater numbers and unformatted SSNs
        patterns = [
            Pattern(
                "6-digit or greater number",
                r"\b\d{6,}\b",
                0.4,
            ),
            Pattern(
                "Unformatted SSN",
                r"\b\d{3}\d{2}\d{4}\b",
                0.9,
            ),
            # Pattern 2: US date formats
            Pattern(
                "US Date Format (dd/mm/yyyy)",
                r"\b\d{2}[-/.]\d{2}[-/.]\d{4}\b",
                0.7,
            ),
        ]

        # Load ICD-9 and ICD-10 patterns using parallel processing
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(LowThresholdHIPAARecognizer.load_icd9_data): 'ICD-9',
                executor.submit(LowThresholdHIPAARecognizer.load_icd10_data): 'ICD-10'
            }
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    patterns.extend(result)
                except Exception as e:
                    print(f"Error loading {futures[future]} data: {e}")

        return patterns

    @staticmethod
    def _load_context() -> List[str]:
        return [
            "date of birth",
            "dob",
            "date of service",
            "dos",
            "icd-9",
            "icd-10",
        ]

    @staticmethod
    def load_icd9_data() -> List[Pattern]:
        """
        Load ICD-9 patterns lazily from a CSV file.
        """
        icd9_patterns = []
        base_file_path = '/usr/bin/data/'
        icd9_file_path = os.path.join(base_file_path, 'ValidICD9-Jan2024.csv')

        # Read ICD-9 data from CSV file
        df_icd9 = pd.read_csv(icd9_file_path, usecols=['CODE', 'LONG DESCRIPTION (VALID ICD-9 FY2024)'])
        for _, row in df_icd9.iterrows():
            code = str(row['CODE'])
            description = re.escape(str(row['LONG DESCRIPTION (VALID ICD-9 FY2024)']))
            pattern = Pattern(
                f"ICD-9 Code: {code}",
                fr"\b{code}\b|\b{description}\b",
                0.8,
            )
            icd9_patterns.append(pattern)
        return icd9_patterns

    @staticmethod
    def load_icd10_data() -> List[Pattern]:
        """
        Load ICD-10 patterns lazily from a CSV file.
        """
        icd10_patterns = []
        base_file_path = '/usr/bin/data/'
        icd10_file_path = os.path.join(base_file_path, 'ValidICD10-Jan2024.csv')

        # Read ICD-10 data from CSV file
        df_icd10 = pd.read_csv(icd10_file_path, usecols=['CODE', 'SHORT DESCRIPTION (VALID ICD-10 FY2024)', 'LONG DESCRIPTION (VALID ICD-10 FY2024)'])
        for _, row in df_icd10.iterrows():
            code = str(row['CODE'])
            description_short = re.escape(str(row['SHORT DESCRIPTION (VALID ICD-10 FY2024)']))
            description_long = re.escape(str(row['LONG DESCRIPTION (VALID ICD-10 FY2024)']))
            pattern = Pattern(
                f"ICD-10 Code: {code}",
                fr"\b{code}\b|\b{description_short}\b|\b{description_long}\b",
                0.8,
            )
            icd10_patterns.append(pattern)
        return icd10_patterns

# Example usage
# if __name__ == "__main__":
#     recognizer = LowThresholdHIPAARecognizer()

#     test_texts = [
#         "Patient's SSN is 123456789",
#         "Date of Birth: 12/05/1985",
#         "Patient diagnosed with Cholera due to Vibrio cholerae 01, biovar cholerae",
#         "ICD-9 Code 0010: Cholera due to vibrio cholerae",
#         "DOS: 03-12-2020"
#     ]

#     for text in test_texts:
#         results = recognizer.analyze(text, entities=["LOW_THRESHOLD_HIPAA"], language="en")
#         for result in results:
#             print(f"Entity: {result.entity_type}, Text: {text[result.start:result.end]}, Confidence Score: {result.score}")
