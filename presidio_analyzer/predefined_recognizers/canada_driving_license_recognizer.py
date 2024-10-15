from typing import Optional, List
from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult

class CanadaDriversLicenceRecognizer(PatternRecognizer):
    """
    Recognizes Canadian driver licenses using regex patterns.
    Scores are assigned based on specific formats:
    - Province name followed by an 8-digit number: 0.4
    - 8-digit number followed by "license number": 0.85
    - 8-digit number followed by a short province name and "license number": 1.0
    """

    PATTERNS = [
        Pattern(
            "Province name followed by 8 digits (weak)",
            r"\b([A-Za-z]+)\s+([0-9]{8})\b",
            0.4,
        ),
        Pattern(
            "8 digits followed by 'license number' (moderate)",
            r"\b([0-9]{8})\s+(license number)\b",
            0.85,
        ),
        Pattern(
            "8 digits followed by province abbreviation and 'license number' (strong)",
            r"\b([0-9]{8})\s+(sk|ab|bc|mb|nb|nl|ns|nt|nu|on|pe|qc|yt)\s+(license number)\b",
            1.0,
        ),
        # 8 digits followed by full province name and 'license number'
        Pattern(
            "8 digits followed by full province name and 'license number' (strong)",
            r"\b([0-9]{8})\s+(Saskatchewan|Alberta|British Columbia|Manitoba|Newfoundland and Labrador|Nova Scotia|Ontario|Quebec|Yukon)\s+(license number)\b",
            1.0,
        ),
        # contain string "license" or "license number", province name and 8 digit number
        Pattern(
            "Contains 'license' or 'license number', province name, and 8-digit number (strong)",
            r"\b(?=.*\b(license|license number)\b)(?=.*\b(Saskatchewan|Alberta|British Columbia|Manitoba|Newfoundland and Labrador|Nova Scotia|Ontario|Quebec|Yukon|Northwest Territories|Nunavut|Prince Edward Island|New Brunswick|SK|AB|BC|MB|NL|NS|NT|NU|ON|PE|QC|YT)\b)(?=.*\b[0-9]{8}\b).*\b",
            1.0,
        ),
        # New pattern for 8-digit number only
        Pattern(
            "8 digits only (weak)",
            r"\b([0-9]{8})\b",
            0.1,
        ),
        # Quebec: one letter, twelve digits
        Pattern(
            name="Quebec License",
            regex=r"\b([A-Za-z]\d{12})\b",
            score=0.9,
        ),
        # Quebec: license number with province name (before or after)
        Pattern(
            name="Quebec License with Province Name",
            regex=r"\b((Quebec|QC)\s+[A-Za-z]\d{12}|[A-Za-z]\d{12}\s+(Quebec|QC))\b",
            score=0.9,
        ),
        Pattern(
            name="PEI License",
            regex=r"\b(\d{5,6})\b",
            score=0.5,
        ),
        # PEI: license number with province name (before or after)
        Pattern(
            name="PEI License with Province Name",
            regex=r"\b((Prince\sEdward\sIsland|PE|PEI)\s+\d{5,6}|\d{5,6}\s+(Prince\sEdward\sIsland|PE|PEI))\b",
            score=0.9,
        ),
        # Ontario: one letter, four digits, optional hyphen, five digits, one digit, 
        # one digit (0, 1, 5, or 6), one digit, one digit (0, 1, 2, or 3), one digit
        Pattern(
            name="Ontario License with Province Name or Abbreviation",
            regex=r"(?:Ontario|ON)?\s*(?:license number|license|DL|Driving license number)?\s*([A-Z]\d{4}-?\d{5}-?\d{4}|[A-Z]\d{9}\d[0156]\d[0123])",
            score=0.95,  # High confidence score
        ),
        Pattern(
            name="Nova Scotia License with Province Name or Abbreviation",
            regex=r"(?:Nova\sScotia|NS).*?(?:license\snumber|DL|license|Driving\slicense\snumber)\s*(?:\w{5}(?:-\d[0123]\d{6})?)",
            score=0.95,  # High confidence score
        ),
        Pattern(
            name="Newfoundland/Labrador License with Province Name or Abbreviation",
            regex=r"(?i)(Newfoundland\/Labrador|NL).*?(?:license|DL|Driving\slicense\snumber).*?\b[A-Z]\d{9}\b",
            score=0.95,  # High confidence score
        ),
        Pattern(
            name="New Brunswick License with Province Name or Abbreviation",
            regex=r"(?i)\b(?:New\sBrunswick|NB)\b.*?\b(?:license\snumber|DL|license|Driving\slicense\snumber)\b.*?\b\d{5,7}\b",
            score=0.95,  # High confidence score
        ),
        Pattern(
            name="Manitoba License with Province Name or Abbreviation",
            regex=r"(?i)(Manitoba|MB|license number|DL|license|Driving\slicense\snumber).*?\b[A-Z]{2}-?[A-Z]{2}-?[A-Z]{2}-?[A-Z][0-9]{3}[A-Z]{2}\b",
            score=0.95,  # High confidence score
        ),
        Pattern(
            name="British Columbia License with Province Name or Abbreviation",
            regex=r"(?:British\sColumbia|BC|license\snumber|DL|license|Driving\slicense\snumber)\D*(\d{7})",
            score=0.95,  # High confidence score
        ),
        Pattern(
            name="Alberta License with Province Name or Abbreviation",
            regex=r"(?i)(?:Alberta|AB).*(?:license number|DL|license|Driving license number).*(?:\d{6}-\d{3}|\d{5,9})",
            score=0.95,  # High confidence score
        ),
    ]

    CONTEXT = [
        "driver",
        "license",
        "permit",
        "identification",
        "province",
        "canadian",
        "driving license number",
        "DL",
        "driver's license",
        "driving permit",
        "provincial",
        "license number",
        "DLN"
    ]


    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "CANADA_DRIVERS_LICENCE",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            supported_language=supported_language,
            patterns=patterns,
            context=context,
        )

    
    def analyze(self, text: str, entities: Optional[List[str]] = None, nlp_artifacts=None) -> List[RecognizerResult]:
        results = super().analyze(text, entities, nlp_artifacts)

        # Filter overlapping results by keeping only the highest confidence one
        filtered_results = []
        for result in results:
            overlap = False
            for fr in filtered_results:
                if (fr.start <= result.start < fr.end) or (result.start <= fr.start < result.end):
                    # If there's an overlap, keep the one with the higher score
                    overlap = True
                    if result.score > fr.score:
                        fr.start = result.start
                        fr.end = result.end
                        fr.score = result.score
            if not overlap:
                filtered_results.append(result)

        return filtered_results

