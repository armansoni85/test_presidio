from typing import Optional, List
from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult, EntityRecognizer


class MedicalRecordNumberRecognizer(PatternRecognizer):
    """
    Recognizes Medical Record Numbers (MRN).

    This recognizer identifies MRNs by searching for phrases such as
    "Medical Record Number", "Person Number", or "MRN" (not case-sensitive)
    followed by a 6-digit number within close proximity.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "MRN with context",
            r"(?:(Medical\sRecord\sNumber|Person\sNumber|MRN)\s[0-9]{6})",
            0.9,  # Higher confidence when context is directly matched
        ),
        Pattern(
            "MRN without context",
            r"\b[0-9]{6}\b",  # MRN without context has a lower confidence
            0.5,
        ),
    ]

    CONTEXT = [
        "medical record number",
        "person number",
        "mrn",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "MRN",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def enhance_pattern_result(self, text: str, pattern_result: RecognizerResult) -> Optional[RecognizerResult]:
        """
        Enhance result confidence based on the proximity of context words.
        """
        for context_word in self.CONTEXT:
            if context_word.lower() in text[max(0, pattern_result.start-20):pattern_result.end+20].lower():
                pattern_result.score += 0.1  # Boost score if context is nearby
                pattern_result.score = min(pattern_result.score, 1.0)  # Cap at 1.0
        return pattern_result