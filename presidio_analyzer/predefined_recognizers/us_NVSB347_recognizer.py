import re
from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult
from typing import List, Optional

class NevadaRecognizer(PatternRecognizer):
    """
    Recognizer for detecting Nevada-specific personal data including Credit Card Numbers (CCN),
    Credit Card Track Data, Social Security Numbers (SSN), and Nevada Driver's License Numbers.
    """

    # Patterns for detecting Nevada-based personal data
    NEVADA_CREDIT_CARD_PATTERN = r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})(?:[-\s]?[0-9]{4})?\b"
    NEVADA_SSN_PATTERN = r"\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b"
    NEVADA_DL_PATTERN = r"\bNevada\sDriver'?s?\sLicense[:\s]?[A-Z0-9]{9}\b"  # Pattern for Nevada Driver's License
    NEVADA_CC_TRACK_DATA_PATTERN = r'Name\s*:\s*"(?P<name>[\w\s]+)"\s*CCN\s*:\s*"(?P<ccn>\d+)"\s*Expiry\s*:\s*"(?P<expiry>\d{2}/\d{2})"\s*CVV\s*:\s*"(?P<cvv>\d{3})"'

    # Context keywords to improve detection accuracy
    CONTEXT_TERMS: List[str] = [
        "credit card", "ccn", "account number", "payment card",
        "social security", "ssn", "driver's license", "nevada",
        "nv dl", "nevada driver license", "nevada dl", "cc track data"
    ]

    def __init__(self, supported_language: Optional[str] = None):
        patterns = [
            Pattern("Nevada Credit Card Number", self.NEVADA_CREDIT_CARD_PATTERN, 0.85),
            Pattern("Nevada SSN", self.NEVADA_SSN_PATTERN, 0.9),
            Pattern("Nevada Driver's License", self.NEVADA_DL_PATTERN, 0.85),
            Pattern("Nevada Credit Card Track Data", self.NEVADA_CC_TRACK_DATA_PATTERN, 0.95)
        ]
        super().__init__(
            supported_entity="US_NVSB347",
            patterns=patterns,
            context=self.CONTEXT_TERMS,
            supported_language=supported_language
        )

    def validate_ccn(self, ccn: str) -> bool:
        """
        Validate credit card number using the Luhn algorithm.
        """
        def luhn_checksum(card_number: str) -> bool:
            def digits_of(n):
                return [int(d) for d in str(n)]
            digits = digits_of(card_number)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d * 2))
            return checksum % 10 == 0

        cleaned_ccn = re.sub(r"\D", "", ccn)  # Remove non-digit characters
        return luhn_checksum(cleaned_ccn)

# Sample input text
# text = """
# Bob Smith's credit card number is 4111-1111-1111-1111 and his Nevada Driver's License number is Nevada DL: A12345678.
# Additionally, his SSN is 123-45-6789. His credit card track data includes:
# Name: "Bob Smith", CCN: "4111111111111111", Expiry: "12/24", CVV: "123".
# """
