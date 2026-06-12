import unicodedata
import re

class NameNormalizer:
    """Utility for cleaning and normalizing football entity names."""

    @staticmethod
    def normalize(name: str) -> str:
        """
        Clean name: lowercase, trim, remove accents, remove extra whitespace.
        Example: "M. Salah " -> "m salah", "Özil" -> "ozil"
        """
        if not name:
            return ''
        name = name.lower().strip()
        name = ''.join((c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn'))
        name = re.sub('[^\\w\\s]', ' ', name)
        name = re.sub('\\s+', ' ', name).strip()
        return name