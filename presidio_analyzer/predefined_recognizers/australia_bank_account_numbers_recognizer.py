from typing import Optional, List
from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult
import re

class AustraliaBankAccountRecognizer(PatternRecognizer):
    """
    Recognizes Australian Bank Account Numbers and BSB codes.
    """

    # Known BSB numbers
    KNOWN_BSB_NUMBERS = set([
        "012-785", "012-911", "013-961", "016-936", "016-985", "032-139", "033-141", "035-825",
        "062-136", "062-707", "062-904", "064-159", "085-645", "087-600", "105-069", "105-083", 
        "105-110", "105-133", "105-141", "105-146", "105-152", "257-019", "257-028", "257-037", 
        "257-046", "257-055", "257-064", "257-073", "257-082", "257-091", "257-100", "257-109", 
        "257-118", "257-127", "257-136", "257-145", "257-154", "257-163", "257-172", "257-181", 
        "257-190", "257-199", "257-208", "257-217", "257-235", "257-244", "257-253", "257-262", 
        "257-271", "257-280", "257-289", "257-298", "482-158", "482-160", "484-095", "484-113", 
        "484-121", "484-122", "484-123", "484-129", "484-133", "484-191", "484-192", "484-193", 
        "484-194", "484-482", "484-552", "484-799", "484-888", "484-911", "484-915", "732-139", 
        "733-141", "762-136", "762-707", "762-904", "764-159", "802-887", "803-110", "803-136", 
        "803-420", "803-421", "807-125", "807-126", "808-269", "808-270", "808-271", "808-272", 
        "808-273", "808-274", "808-275", "808-276", "808-277"
    ])

    PATTERNS = [
        # BSB code followed by account number (high confidence)
        Pattern(
            "Australia Bank Account Number with BSB",
            r"\b(\d{3}-\d{3})-(\d{6,10})(?!\d)\b",  # Match BSB with account number
            0.85,
        ),
        # Account number without BSB (medium confidence)
        Pattern(
            "Australia Bank Account Number",
            r"\b\d{6,10}(?!\d)\b",  # Six to ten digits without BSB, followed by non-digit
            0.5,
        ),
        # BSB code alone (high confidence)
        Pattern(
            "BSB Code",
            r"\b(\d{3}-\d{3})(?!-\d{3})\b",  # Prevents matching with patterns that have more digits
            0.8,
        ),
    ]

    CONTEXT = [
        "bank account",
        "account number",
        "Australia bank account number",
        "Acct Num",
        "swift bank code",
        "correspondent bank",
        "base currency",
        "Australia bank account",
        "account holder ",
        "bank address",
        "information account",
        "fund transfers",
        "bank charges",
        "bank details",
        "banking information",
        "account number with bsb",
        "acc no. with bsb code",
    ]

    # Introduce negative context for filtering out false positives
    NEGATIVE_CONTEXT = [
        "driver",
        "license",
        "identification",
        "permit",
        "licence",
    ]
    
    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "AUSTRALIA_BANK_ACCOUNT",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def _match_known_bsb(self, bsb_number: str) -> float:
        """
        Match the BSB number against known BSB numbers and return a confidence score.
        """
        if bsb_number in self.KNOWN_BSB_NUMBERS:
            return 1.0
        return 0.5

    def analyze(self, text: str, entities: Optional[List[str]] = None, nlp_artifacts=None) -> List[RecognizerResult]:
        results = super().analyze(text, entities, nlp_artifacts)
        updated_results = []

        for result in results:
            # Apply context-based scoring adjustment
            if not any(context_word in text.lower() for context_word in self.CONTEXT):
                result.score *= 0.3  # Significant reduction if context is missing
            
            # Reduce score or eliminate result if negative context is detected
            if any(neg_context_word in text.lower() for neg_context_word in self.NEGATIVE_CONTEXT):
                result.score *= 0.15  # Significant reduction if negative context is found
            
            # Additional BSB number matching logic
            if result.entity_type == "AUSTRALIA_BANK_ACCOUNT":
                match = re.search(r"(\d{3}-\d{3})-(\d{6,10})", text[result.start:result.end])
                if match:
                    bsb_number = match.group(1)
                    confidence = self._match_known_bsb(bsb_number)
                    result.score = confidence
            
            # Only keep results with a significant confidence score
            if result.score > 0.3:
                updated_results.append(result)

        return updated_results