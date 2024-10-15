from typing import Optional, List
from presidio_analyzer import Pattern, PatternRecognizer

class FerpaRecognizer(PatternRecognizer):
    """
    Recognizes FERPA (Family Educational Rights and Privacy Act) related information 
    using regex patterns and context words.
    
    This recognizer identifies FERPA-related terms using custom patterns and contexts.
    Reference: FERPA rules provided in Ferpa.txt.
    """

    # Define regex patterns that match expressions from Ferpa.txt
    PATTERNS = [
        Pattern(
            "FERPA Student ID or Number", 
            r"(?i)\b(FERPA).*(student|id|identification)\s?(number|num|no|nbr)\b(?!.*(member|parcel|invoice|sra|pa id|tx|vat|vin|vehicle|insurance|transaction|medicade|seller|benefit|caller|tax|taxpayer|employer|employee|loan|sample|docket))", 
            0.85
        ),
        Pattern(
            "FERPA Student ID with Name", 
            r"(?i)(student|id|identification)\s?(number|num|no|nbr).*(first name|last name|student name|record)\b(?!.*(member|parcel|invoice|sra|pa id|tx|vat|vin|vehicle|insurance|transaction|medicade|seller|benefit|caller|tax|taxpayer|employer|employee|loan|sample|docket))",
            0.85
        ),
        Pattern(
            "FERPA Student Name with Date of Birth", 
            r"(?i)(student name|student id|identification).*(date of birth|birthdate).*(19\d{2}|20\d{2}|\d{1,2}[-/]\d{1,2}[-/]\d{4})(?!.*(member|parcel|invoice|sra|pa|tx|vat|vin|caller|tax|taxpayer|employer|employee|loan|sample|docket))", 
            0.85
        ),
        Pattern(
            "FERPA GPA with Transcript or Academic Record", 
            r"(?i)(grade point average|gpa).{0,2}=\.*.*(transcript|academic record)\b", 
            0.85
        ),
        Pattern(
            "FERPA Disciplinary Records", 
            r"(?i)(discipline|disciplinary).*(student|id|identification)\s?(number|num|no|nbr)\b", 
            0.85
        )
    ]

    CONTEXT = [
        "FERPA",
        "student",
        "student ID",
        "identification number",
        "birthdate",
        "grade point average",
        "transcript",
        "academic record",
        "disciplinary record"
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "FERPA",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
