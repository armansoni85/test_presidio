from typing import Optional, List
from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult
import logging
import re

logger = logging.getLogger("presidio-analyzer")

class SpainDNIRecognizer(PatternRecognizer):
    logger.info("Initializing Spain DNI Recognizer...")

    # Define patterns for Spain DNI
    # Format: 8 digits followed by a letter (checksum character)
    PATTERNS = [
        Pattern(
            "Spain DNI - High Confidence",
            r"\b\d{8}[A-HJ-NP-TV-Z]\b",  # DNI: 8 digits followed by one checksum letter
            0.7  # Initial confidence score
        ),
    ]

    # Context keywords for Spain DNI in both Spanish and English
    CONTEXT = [
        "DNI", "Documento Nacional de Identidad", "national ID", 
        "identificación nacional", "número de identificación", 
        "identification number", "national identification"
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "es",  # Supports Spanish and English
        supported_entity: str = "SPAIN_DNI",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def analyze(
        self, text: str, entities: List[str], nlp_artifacts=None
    ) -> List[RecognizerResult]:
        results = super().analyze(text, entities, nlp_artifacts)
        for result in results:
            # Apply checksum validation for the DNI
            dni = text[result.start:result.end]
            if self._validate_dni_checksum(dni):
                result.score = self._adjust_score_based_on_context(text, result)
            else:
                result.score = 0.0  # Set confidence to 0 if checksum fails
        return results

    def _validate_dni_checksum(self, dni: str) -> bool:
        """ Validate the DNI checksum. """
        dni_number = dni[:-1]  # Extract the 8 digits
        dni_letter = dni[-1]   # Extract the checksum letter
        valid_letters = "TRWAGMYFPDXBNJZSQVHLCKE"
        
        # DNI letter is based on a mod 23 operation of the digits
        try:
            mod_value = int(dni_number) % 23
            return valid_letters[mod_value] == dni_letter
        except ValueError:
            return False

    def _adjust_score_based_on_context(self, text: str, result: RecognizerResult) -> float:
        """ Adjust the score based on the presence of context keywords. """
        if any(keyword.lower() in text.lower() for keyword in self.CONTEXT):
            return min(result.score + 0.3, 1.0)  # High confidence if context is present
        return result.score  # Medium confidence if no context is found
