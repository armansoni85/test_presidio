from presidio_analyzer import PatternRecognizer, Pattern
import re
from typing import List, Optional

class USDriversLicenseRecognizer(PatternRecognizer):
    # Define patterns for US Driver's License numbers
    PATTERNS = [
        Pattern("US Driver's License (generic)", r"\b(?:[A-Z0-9]{1,9})\b", 0.5)
    ]

    # Keywords and state names to raise confidence scores
    KEYWORDS = [
        'driver\'s license', 'DL', 'permit', 'license', 'identification'
    ]

    STATES = [
        'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 
        'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 
        'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 
        'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 
        'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 
        'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 
        'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 
        'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 
        'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'
    ]

    def __init__(self, supported_language: Optional[str] = None):
        super().__init__(
            supported_entity="US_DRIVERS_LICENSE",
            supported_language=supported_language,
            patterns=self.PATTERNS,
            context=None
        )

    def enhance_confidence(self, text, pattern_result):
        """
        Enhance confidence based on proximity to keywords and state names.
        """
        context_window = 50  # Check within 50 characters before and after
        start, end = pattern_result.start, pattern_result.end
        surrounding_text = text[max(0, start - context_window):min(len(text), end + context_window)].lower()

        # Check for keywords and state names in proximity
        keyword_present = any(keyword.lower() in surrounding_text for keyword in self.KEYWORDS)
        state_present = any(state.lower() in surrounding_text for state in self.STATES)

        # Adjust confidence levels based on the proximity of keywords and states
        if keyword_present and state_present:
            pattern_result.score = 1.0  # High confidence
        elif keyword_present:
            pattern_result.score = 0.75  # Medium confidence
        elif state_present:
            pattern_result.score = 0.5  # Low confidence
        else:
            pattern_result.score = 0.25  # Very low confidence

        return pattern_result

    def analyze(self, text, entities, nlp_artifacts=None):
        """
        Override the analyze method to enhance results with contextual information.
        """
        results = super().analyze(text, entities, nlp_artifacts)
        enhanced_results = [self.enhance_confidence(text, result) for result in results]
        return enhanced_results
