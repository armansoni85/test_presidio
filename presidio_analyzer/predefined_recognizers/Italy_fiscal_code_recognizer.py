from typing import Optional, List
from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult
import logging
import re

logger = logging.getLogger("presidio-analyzer")

class ItalyFiscalCodeRecognizer(PatternRecognizer):
    logger.info("Initializing Italy Fiscal Code Recognizer...")

    # Define the pattern for the Italian fiscal code
    PATTERNS = [
        Pattern(
            "Italy Fiscal Code - High Confidence",
            r"(?i:\b[A-Z]{3}[ -]?[A-Z]{3}[ -]?[0-9]{2}[A-EHLMPRST](?:[04][1-9]|[1256][0-9]|[37][01])[ -]?[A-MZ][0-9]{3}[A-Z]\b)",
            1.0,  # Initial confidence score for the pattern match
        ),
        Pattern(
            "Italy Fiscal Code - Medium Confidence",
            r"^([B-DF-HJ-NP-TV-Z]{3})([B-DF-HJ-NP-TV-Z]{3})(\d{2})([A-EHLMPR-T])(\d{2})(\d{4})(\d)$",
            0.7,  # Initial confidence score for the pattern match
        ),
    ]

    # Context keywords for Italy fiscal codes
    CONTEXT = [
        "codice fiscale", "fiscal code", "italian tax code", "italy personal code"
    ]

    # Character values for checksum calculation
    ODD_VALUES = {
        **{char: val for char, val in zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ', [1, 0, 5, 7, 9, 13, 15, 17, 19, 21, 2, 4, 18, 20, 11, 3, 6, 8, 12, 14, 16, 10, 22, 25, 24, 23])},
        **{str(digit): val for digit, val in zip('0123456789', [1, 0, 5, 7, 9, 13, 15, 17, 19, 21])}
    }
    
    EVEN_VALUES = {
        **{char: val for char, val in zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ', range(26))},
        **{str(digit): int(digit) for digit in '0123456789'}
    }

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "it",  # Supports Italian and English
        supported_entity: str = "ITALY_FISCAL_CODE",
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
            # Check if the fiscal code has a valid checksum
            code = re.sub(r'[^A-Z0-9]', '', result.entity_type)  # Remove spaces or hyphens
            if self._validate_checksum(code):
                result.score = 1.0  # High confidence for valid fiscal code
            else:
                result.score = 0.0  # Invalid fiscal code

            # Increase the score if context keywords are found
            if any(keyword.lower() in text.lower() for keyword in self.CONTEXT):
                result.score = min(result.score + 0.3, 1.0)  # Increase score by 0.3, cap at 1.0
        return results

    def _validate_checksum(self, code: str) -> bool:
        """
        Validates the checksum for the given Italian fiscal code.
        """
        if len(code) != 16:
            return False

        # Calculate checksum
        checksum_sum = 0
        for i, char in enumerate(code[:-1]):
            if i % 2 == 0:  # Odd positions (0-indexed)
                checksum_sum += self.ODD_VALUES[char]
            else:  # Even positions
                checksum_sum += self.EVEN_VALUES[char]

        # Calculate checksum character
        checksum_char = chr((checksum_sum % 26) + ord('A'))
        
        # Validate checksum
        return checksum_char == code[-1]

