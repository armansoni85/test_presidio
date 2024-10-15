import re
from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts
from typing import List, Optional

class CCTrackDataRecognizer(PatternRecognizer):
    """
    Recognizer for detecting Credit Card Track Data (Track-1 and Track-2) in text.
    """

    # Credit Card Number (CCN) patterns for Track-1 and Track-2
    CREDIT_CARD_PATTERN = r"\b(?:\d{4}[- ]?){3}\d{4}\b"  # Basic CCN pattern (can be expanded for issuer-specific patterns)
    
    # Expiry Date pattern (MM/YY or MM/YYYY)
    EXPIRY_DATE_PATTERN = r"(0[1-9]|1[0-2])\/?([0-9]{2}|[0-9]{4})"

    # Common context terms related to credit card details
    CONTEXT_TERMS: List[str] = ["credit card", "card number", "expiry date", "cvv", "track-1", "track-2", "name"]

    def __init__(self, supported_language: Optional[str] = None):
        patterns = [
            Pattern("Credit Card Number", self.CREDIT_CARD_PATTERN, 0.85),
            Pattern("Expiry Date", self.EXPIRY_DATE_PATTERN, 0.8)
        ]
        super().__init__(
            supported_entity="CREDIT_CARD_TRACK_DATA",
            patterns=patterns,
            context=self.CONTEXT_TERMS,
            supported_language=supported_language
        )

    def analyze(self, text: str, entities: List[str], nlp_artifacts: Optional[NlpArtifacts] = None) -> List[RecognizerResult]:
        """
        Analyze method to detect credit card track data in text.
        """
        # Call the base analyze method to detect the initial patterns
        results = super().analyze(text, entities, nlp_artifacts)

        # Presidio NLP for Name detection (using Spacy's 'label_' for the entity type)
        if nlp_artifacts and nlp_artifacts.entities:
            for entity in nlp_artifacts.entities:
                # Spacy entities use 'label_' for entity type, and 'start_char', 'end_char' for span positions
                if entity.label_ == "PERSON":  # Assuming 'PERSON' is the label for name entities
                    results.append(
                        RecognizerResult(
                            entity_type="PERSON",
                            start=entity.start_char,
                            end=entity.end_char,
                            score=0.85
                        )
                    )

        # Ensure that the recognizer returns results if at least 3 track data hits are found
        valid_results = []
        track_data_count = 0
        for result in results:
            # Validate each result with custom validation logic
            if self.custom_validate_result(result, text):
                valid_results.append(result)
                if result.entity_type in ["CREDIT_CARD_TRACK_DATA", "PERSON"]:
                    track_data_count += 1

        if track_data_count >= 3:
            return valid_results
        else:
            return []  # Return empty if less than 3 hits

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

    def custom_validate_result(self, result: RecognizerResult, text: str) -> bool:
        """
        Custom validation for credit card numbers in the result using the Luhn algorithm.
        """
        matched_text = text[result.start:result.end]
        if result.entity_type == "CREDIT_CARD_TRACK_DATA":
            return self.validate_ccn(matched_text)
        return True
