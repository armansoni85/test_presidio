import re
from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult
from typing import List, Optional

class CreditCardIssuerRecognizer(PatternRecognizer):
    """
    Recognizer for Credit Card numbers by issuer using regex patterns.
    """

    # Supported Credit Card Issuers
    CREDIT_CARD_ISSUERS = {
        "Visa": r"4[0-9]{12}(?:[0-9]{3})?",  # Visa card numbers start with 4, 13 or 16 digits
        "MasterCard": r"5[1-5][0-9]{14}",  # MasterCard numbers start with 51-55, 16 digits
        "American Express": r"3[47][0-9]{13}",  # Amex numbers start with 34 or 37, 15 digits
        "Diners Club": r"3(?:0[0-5]|[68][0-9])[0-9]{11}",  # Diners Club numbers start with 300-305, 36 or 38, 14 digits
        "Discover": r"6(?:011|5[0-9]{2})[0-9]{12}",  # Discover card numbers start with 6011, 622126-622925, 644-649, 65, 16 digits
        "JCB": r"(?:2131|1800|35\d{3})\d{11}"  # JCB cards start with 2131, 1800, or 35 (16-19 digits)
    }

    CONTEXT_TERMS: List[str] = [
        "credit card", "card number", "card no", "cc#", "card holder"
    ]

    def __init__(self, supported_language: Optional[str] = None):
        patterns = [
            Pattern(f"{issuer} Credit Card", pattern, 0.85)
            for issuer, pattern in self.CREDIT_CARD_ISSUERS.items()
        ]
        super().__init__(
            supported_entity="CREDIT_CARD_ISSUER",
            patterns=patterns,
            supported_language=supported_language,
            context=self.CONTEXT_TERMS
        )

    def validate_result(self, pattern_text: str) -> bool:
        """
        Validate the credit card number using the Luhn algorithm.
        """
        def luhn_checksum(card_number: str) -> bool:
            # Luhn algorithm to validate credit card numbers
            def digits_of(n):
                return [int(d) for d in str(n)]

            digits = digits_of(card_number)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d * 2))
            return checksum % 10 == 0

        card_number = re.sub(r"\D", "", pattern_text)  # Remove non-digit characters
        return luhn_checksum(card_number)

    def analyze(self, text, entities, nlp_artifacts=None):
        results = super().analyze(text, entities, nlp_artifacts)
        valid_results = []
        for result in results:
            # Extract the matched text using start and end indices
            matched_text = text[result.start:result.end]
            if self.validate_result(matched_text):
                valid_results.append(result)
        return valid_results
