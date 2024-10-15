import re
from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult
from typing import List, Optional

class WashingtonStateRecognizer(PatternRecognizer):
    """
    Recognizer for detecting Washington-specific personal data including Credit Card Numbers,
    Credit Card Track Data, Social Security Numbers, and Washington Driver's License Numbers.
    """

    # Patterns for detecting Washington-specific personal data
    CREDIT_CARD_PATTERN = r"\b(?:(?:card\s*number|credit\s*card|ccn|account\s*number|payment\s*card)\s*[:-]?\s*)?(?:4[0-9]{3}[-\s]?[0-9]{4}[-\s]?[0-9]{4}[-\s]?[0-9]{4}|5[1-5][0-9]{2}[-\s]?[0-9]{4}[-\s]?[0-9]{4}[-\s]?[0-9]{4}|3[47][0-9]{2}[-\s]?[0-9]{6}[-\s]?[0-9]{5}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11})(?:\s*(?:number|credit\s*card|ccn|payment\s*card))?\b"  # Detects credit card numbers with spaces/dashes
    CCN_TRACK_DATA_PATTERN = r'Name\"\s*s\s\d+\s\"(?P<name>[\w\s\-]+)\".*?Credit_Card_Number\"\s*s\s\d+\s\"(?P<ccn>\d+)\".*?Issuer\"\s*s\s\d+\s\"(?P<issuer>\w+)\".*?Expiry[_\s]Date\"\s*s\s\d+\s\"(?P<expiry>\d{2}\\\/\d{2})\".*?cvv\"\s*s\s\d+\s\"(?P<cvv>\d{3})\"'  # Detects structured CCN track data
    WASHINGTON_SSN_PATTERN = r"\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b"  # Detects valid Washington SSNs (same as other U.S. SSNs)
    WASHINGTON_DL_PATTERN = r"\bWDL[A-Z0-9]{9}[A-Z]{2}\b"  # Simplified Washington Driver's License pattern

    # Common context terms related to Washington-based sensitive data
    CONTEXT_TERMS: List[str] = [
        "Washington", "WA", "Washington state", "credit card", "card number", "social security", "SSN",
        "driver's license", "Washington driver's license", "Washington DL", "track data", "CVV", "expiry date"
    ]

    def __init__(self, supported_language: Optional[str] = None):
        patterns = [
            Pattern("Washington Credit Card Number", self.CREDIT_CARD_PATTERN, 0.85),
            Pattern("Washington CCN Track Data", self.CCN_TRACK_DATA_PATTERN, 0.95),
            Pattern("Washington SSN", self.WASHINGTON_SSN_PATTERN, 0.9),
            Pattern("Washington Driver's License", self.WASHINGTON_DL_PATTERN, 0.8)
        ]
        super().__init__(
            supported_entity="US_WASB6043",
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
# Bob Smith from Washington has the following information to report. 
# His credit card number is 4316020000630490 and Washington driver's license WDL123456789AA. 
# He reports his social security number is 260-53-2093. Additionally, his credit card track data: 
# Name: "John Doe", Credit_Card_Number: "5500005555555559", Issuer: "Mastercard", Expiry_Date: "12/29", CVV: "123".
# """
