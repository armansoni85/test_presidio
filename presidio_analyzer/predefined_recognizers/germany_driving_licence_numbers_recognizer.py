from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult
from typing import List, Optional
import re

class GermanDriversLicenseRecognizer(PatternRecognizer):
    """
    Recognizer to detect German driver's license numbers based on specific patterns and context.
    """

    # Define the regex pattern for German driver's license numbers
    PATTERNS = [
        Pattern(
            name="German Drivers License",
            regex=r"\b([A-Za-z0-9]{1})(\d{2})([A-Za-z0-9]{6})(\d)([A-Za-z0-9]{1})\b",
            score=0.5,  # Base score before context checks
        ),
    ]

    # Define the keywords to increase confidence of detection
    CONTEXT = [
        "ausstellungsdatum", "ausstellungsort", "ausstellende behöde", "ausstellende behorde",
        "ausstellende behoerde", "führerschein", "fuhrerschein", "fuehrerschein", "führerscheinnummer",
        "fuhrerscheinnummer", "fuehrerscheinnummer", "führerschein-", "fuhrerschein-", "fuehrerschein-",
        "führerscheinnummernr", "fuhrerscheinnummernr", "fuehrerscheinnummernr", "führerscheinnummerklasse",
        "fuhrerscheinnummerklasse", "fuehrerscheinnummerklasse", "nr-führerschein", "nr-fuhrerschein",
        "nr-fuehrerschein", "no-führerschein", "no-fuhrerschein", "no-fuehrerschein", "n-führerschein",
        "n-fuhrerschein", "n-fuehrerschein", "permis de conduire", "driverlic", "driverlics", "driverlicense",
        "driverlicenses", "driverlicence", "driverlicences", "driver lic", "driver lics", "driver license",
        "driver licenses", "driver licence", "driver licences", "driverslic", "driverslics", "driverslicence",
        "driverslicences", "driverslicense", "driverslicenses", "drivers lic", "drivers lics", "drivers license",
        "drivers licenses", "drivers licence", "drivers licences", "driver'lic", "driver'lics", "driver'license",
        "driver'licenses", "driver'licence", "driver'licences", "driver' lic", "driver' lics", "driver' license",
        "driver' licenses", "driver' licence", "driver' licences", "driver'slic", "driver'slics", "driver'slicense",
        "driver'slicenses", "driver'slicence", "driver'slicences", "driver's lic", "driver's lics", "driver's license",
        "driver's licenses", "driver's licence", "driver's licences", "dl#", "dls#", "driverlic#", "driverlics#",
        "driverlicense#", "driverlicenses#", "driverlicence#", "driverlicences#", "driver lic#", "driver lics#",
        "driver license#", "driver licenses#", "driver licences#", "driverslic#", "driverslics#", "driverslicense#",
        "driverslicenses#", "driverslicence#", "driverslicences#", "drivers lic#", "drivers lics#", "drivers license#",
        "drivers licenses#", "drivers licence#", "drivers licences#", "driver'lic#", "driver'lics#", "driver'license#",
        "driver'licenses#", "driver'licence#", "driver'licences#", "driver' lic#", "driver' lics#", "driver' license#",
        "driver' licenses#", "driver' licence#", "driver' licences#", "driver'slic#", "driver'slics#", "driver'slicense#",
        "driver'slicenses#", "driver'slicence#", "driver'slicences#", "driver's lic#", "driver's lics#", "driver's license#",
        "driver's licenses#", "driver's licence#", "driver's licences#", "driving licence", "driving license", "dlno#", "driv lic",
        "driv licen", "driv license", "driv licenses", "driv licence", "driv licences", "driver licen", "drivers licen",
        "driver's licen", "driving lic", "driving licen", "driving licenses", "driving licence", "driving licences", "driving permit",
        "dlno"
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "GERMAN_DRIVERS_LICENSE",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def analyze(self, text: str, entities: List[str], nlp_artifacts=None) -> List[RecognizerResult]:
        results = super().analyze(text, entities, nlp_artifacts)
        
        # Apply context-based scoring and checksum validation
        for result in results:
            if self._has_context(text, result.start, result.end):
                if self._checksum_is_valid(text[result.start:result.end]):
                    result.score = min(result.score + 0.4, 1.0)  # Boost score with valid checksum and context
            else:
                result.score = result.score * 0.5  # Reduce score if no context found

        return results

    def _has_context(self, text: str, start: int, end: int) -> bool:
        """Check if there is relevant context around the detected pattern."""
        window_size = 300  # Number of characters to check before and after the detected pattern
        context_window = text[max(0, start - window_size): min(len(text), end + window_size)]
        context_found = any(context_word.lower() in context_window.lower() for context_word in self.CONTEXT)
        return context_found

    def _checksum_is_valid(self, license_number: str) -> bool:
        """
        Validate checksum for German driver's license.
        This is a placeholder for actual checksum logic as it is not clearly defined.
        """
        # Placeholder checksum validation logic: Adjust as needed
        # For demonstration, assume valid if length is 11 and it contains both digits and letters
        has_digits = any(char.isdigit() for char in license_number)
        has_letters = any(char.isalpha() for char in license_number)
        return len(license_number) == 11 and has_digits and has_letters

# Example usage
text = "The driver's license number is B12AB34CDE1 issued by the relevant authority."
recognizer = GermanDriversLicenseRecognizer()
results = recognizer.analyze(text, ["GERMAN_DRIVERS_LICENSE"])

for result in results:
    print(f"Detected: {text[result.start:result.end]}, Score: {result.score}")
