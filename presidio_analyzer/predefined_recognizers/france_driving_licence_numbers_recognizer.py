from typing import Optional, List, Tuple
from presidio_analyzer import Pattern, PatternRecognizer
import re
import logging
logger = logging.getLogger("presidio-analyzer")

class FranceDriversLicenceRecognizer(PatternRecognizer):
    logger.info("France Drivers LicenceRecognizer...............")
    PATTERNS = [
        Pattern(
            "France Driver License",
            r"\b(?=[0-9]*[A-Za-z])[0-9]*[A-Za-z][0-9]*\b",  # Regex pattern to match 12 characters with one alphabet
            0.3,  # Confidence score for the pattern match
        ),
        Pattern(
            "France Driver License",
            r"\b([0-9]{2})(0[1-9]|1[0-2])(0[1-9]|[1-9][0-9]|2[1-9]|2[AaBb])(?!20)([0-9]{6})\b",  # Regex pattern to match 12 characters with two  alphabet
            1.0,  # Confidence score for the pattern match
        ),
    ]
    CONTEXT = ["permis de conduire", "numéro de permis", "licence de conduire"]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "fr",  # French language
        supported_entity: str = "FRANCE_DRIVERS_LICENSE",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )