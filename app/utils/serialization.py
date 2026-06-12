from typing import Any, Dict, List, Union
from bson import ObjectId

class Serialization:
    """Helper for converting MongoDB documents to JSON-friendly formats."""

    @staticmethod
    def fix_ids(obj: Any) -> Any:
        """
        Recursively convert ObjectId fields to strings.
        Handles nested dictionaries and lists.
        """
        if isinstance(obj, list):
            return [Serialization.fix_ids(item) for item in obj]
        if isinstance(obj, dict):
            new_obj = {}
            for key, value in obj.items():
                if key == '_id' and isinstance(value, ObjectId):
                    new_obj[key] = str(value)
                else:
                    new_obj[key] = Serialization.fix_ids(value)
            return new_obj
        if isinstance(obj, ObjectId):
            return str(obj)
        return obj