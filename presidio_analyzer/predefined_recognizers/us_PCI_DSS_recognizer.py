import re
from presidio_analyzer import PatternRecognizer, RecognizerResult, Pattern
from typing import List, Optional

class PCI_DSS_CreditCardAndTrackDataRecognizer(PatternRecognizer):
    """
    Recognizer for detecting Credit Card Numbers (CCN) and Credit Card Track Data.
    A hit in either one will trigger the policy.
    """

    # Credit Card Number (CCN) patterns
    CREDIT_CARD_PATTERN = r"\b(?:\d{4}[- ]?){3}\d{4}\b"  # Basic pattern for 16-digit CCNs

    # Pattern to detect track data components (credit card number, issuer, expiry date)
    TRACK_DATA_PATTERN = r'\"Credit_Card_Number\"\s*s\s*\d+\s*\"(\d{16})\"'

    def __init__(self, supported_language: Optional[str] = None):
        patterns = [
            Pattern("Credit Card Number", self.CREDIT_CARD_PATTERN, 0.85),
            Pattern("Track Data", self.TRACK_DATA_PATTERN, 0.9)
        ]
        super().__init__(
            supported_entity="PCI_DSS_CREDIT_CARD_OR_TRACK_DATA",
            patterns=patterns,
            supported_language=supported_language
        )

    def analyze(self, text: str, entities: List[str], nlp_artifacts=None) -> List[RecognizerResult]:
        """
        Analyze method to detect both credit card numbers and track data in the text.
        """
        results = super().analyze(text, entities, nlp_artifacts)

        # Parse for credit card numbers in structured track data
        track_data_results = self.detect_track_data(text)
        if track_data_results:
            results.extend(track_data_results)

        # Filter out duplicates or return the first relevant hit
        unique_results = self.filter_unique_results(results)

        # Return only the first relevant result
        if len(unique_results) > 0:
            return [unique_results[0]]  # Return only the first result
        else:
            return []  # No hits, return empty list

    def detect_track_data(self, text: str) -> List[RecognizerResult]:
        """
        Detect credit card numbers embedded in structured track data.
        """
        track_data_results = []
        matches = re.finditer(self.TRACK_DATA_PATTERN, text)

        for match in matches:
            credit_card_number = match.group(1)
            start = match.start(1)
            end = match.end(1)

            # Validate the credit card number using the Luhn algorithm
            if self.validate_ccn(credit_card_number):
                track_data_results.append(
                    RecognizerResult(
                        entity_type="CREDIT_CARD_TRACK_DATA",
                        start=start,
                        end=end,
                        score=0.9
                    )
                )

        return track_data_results

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

    def filter_unique_results(self, results: List[RecognizerResult]) -> List[RecognizerResult]:
        """
        Filter out duplicate results by comparing start and end positions.
        """
        unique_results = []
        seen_positions = set()

        for result in results:
            position_key = (result.start, result.end)
            if position_key not in seen_positions:
                unique_results.append(result)
                seen_positions.add(position_key)

        return unique_results
