from typing import Optional, List
from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult
import logging
import re

logger = logging.getLogger("presidio-analyzer")

class FranceVATRecognizer(PatternRecognizer):
    logger.info("Initializing France VAT Recognizer...")

    # Define patterns for France VAT Numbers
    PATTERNS = [
        Pattern(
            "France VAT - 13 Character Alphanumeric",
            r"\bFR[-\s]?[A-Za-z0-9]{2}[-\s,.]?\d{3}[-\s,.]?\d{3}[-\s,.]?\d{3}\b",  # VAT format: FR, 2 letters/digits, 11 digits
            0.5  # Initial confidence score for the pattern match
        ),
        Pattern(
            "France VAT - Alternative Pattern",
            r"\bFR\d{11}\b",  # Alternative VAT format: FR followed by 11 digits
            0.5  # Initial confidence score for the pattern match
        )
    ]

    # Context keywords for VAT Numbers
    CONTEXT = [
        "vat number", "vat no", "vat#", "value added tax", "siren identification no",
        "numéro d'identification", "taxe sur la valeur ajoutée", "n° tva",
        "numéro de tva", "numéro d'identification siren"
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "fr",  # Supports French and English
        supported_entity: str = "FRANCE_VAT",
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
        logger.info(f"Analyzing text for France VAT: {text}")
        results = super().analyze(text, entities, nlp_artifacts)
        for result in results:
            vat_number = text[result.start:result.end]
            logger.debug(f"Detected VAT: {vat_number}, Confidence: {result.score}")

            # Remove spaces and non-alphanumeric characters for checksum validation
            cleaned_vat = re.sub(r"[-\s,.]", "", vat_number)

            # Perform checksum validation
            if self._is_valid_checksum(cleaned_vat):
                logger.info(f"Checksum valid for VAT: {vat_number}")
                result.score = 0.7  # Medium confidence if checksum passes
                if any(keyword in text.lower() for keyword in self.CONTEXT):
                    logger.info(f"Context keywords found for VAT: {vat_number}, setting high confidence.")
                    result.score = 1.0  # High confidence if context keywords are present
            else:
                logger.warning(f"Invalid checksum for VAT: {vat_number}")
                result.score = 0.0  # Invalid VAT number
        return results

    def _is_valid_checksum(self, vat: str) -> bool:
        """
        Validate the VAT checksum using Modulus 97.
        The first two characters "FR" are ignored for the checksum calculation.
        """
        if not vat.startswith("FR") or len(vat) < 13:
            return False

        # Extract the numeric part for validation
        numeric_part = vat[2:]  # Ignore "FR"

        # Perform modulus 97 check on the numeric part
        try:
            return int(numeric_part) % 97 == 0
        except ValueError:
            return False  # Handle cases where the numeric part is not fully numeric
