from typing import Optional, List
from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult
import logging
import re

logger = logging.getLogger("presidio-analyzer")

class EU_IBANRecognizer(PatternRecognizer):
    logger.info("Initializing EU IBAN Recognizer...")

    # Define combined patterns for IBANs used in multiple EU countries
    # This covers country-specific patterns, including a general IBAN format
    PATTERNS = [
        Pattern(
            "EU IBAN - General Pattern",
            r"\b[A-Z]{2}\d{2}(?:[A-Z0-9]{1,4}\s?){4,}\b",  # General IBAN pattern for EU countries
            0.5  # Initial confidence score for the pattern match
        )
    ]

    # Context keywords for IBAN numbers
    CONTEXT = [
        "IBAN", "international bank account number", "numéro de compte", 
        "nummer IBAN", "code IBAN", "identifiant bancaire"
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",  # Supports multiple languages for EU countries
        supported_entity: str = "EU_IBAN",
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
        logger.info(f"Analyzing text for EU IBAN: {text}")
        results = super().analyze(text, entities, nlp_artifacts)
        
        for result in results:
            iban_number = text[result.start:result.end]
            logger.debug(f"Detected IBAN: {iban_number}, Confidence: {result.score}")

            # Remove spaces for checksum validation
            cleaned_iban = re.sub(r"\s+", "", iban_number)

            # Perform checksum validation using the ISO 7064 Mod 97-10 algorithm
            if self._is_valid_checksum(cleaned_iban):
                logger.info(f"Checksum valid for IBAN: {iban_number}")
                result.score = 1.0  # High confidence if checksum passes
            else:
                logger.warning(f"Invalid checksum for IBAN: {iban_number}")
                result.score = 0.0  # Invalid IBAN
        return results

    def _is_valid_checksum(self, iban: str) -> bool:
        """
        Validate the IBAN checksum using the ISO 7064 Mod 97–10 algorithm.
        The first four characters are moved to the end, and letters are converted to numbers.
        """
        # Move the first four characters to the end
        rearranged_iban = iban[4:] + iban[:4]

        # Convert each letter to its corresponding number (A = 10, B = 11, ..., Z = 35)
        numeric_iban = ''.join(str(int(char, 36)) if char.isalpha() else char for char in rearranged_iban)

        # Perform modulus 97 check
        try:
            return int(numeric_iban) % 97 == 1
        except ValueError:
            return False  # Handle the case where the IBAN isn't fully numeric
