import re

class InputSanitizer:
    @staticmethod
    def clean_mood_query(text: str, max_chars: int = 300) -> str:
        """
        Sanitizes raw user input to ensure security and prevent embedding degradation.
        Strips HTML tags, controls character boundaries, and normalizes spacing.
        """
        if not text:
            return ""
        
        # Strip HTML/XML tags
        text = re.sub(r'<[^>]*>', '', text)
        
        # Enforce strict character limit to optimize transformer processing windows
        text = text[:max_chars]
        
        # Normalize multiple spaces, tabs, and newlines into a single space
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text