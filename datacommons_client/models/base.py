from dataclasses import asdict
import json
from typing import Annotated, Any, Dict, Iterable, TypeAlias

from pydantic import BeforeValidator


class SerializableMixin:
  """Provides serialization methods for the Response dataclasses."""

  def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
    """Converts the instance to a dictionary.

        Args:
            exclude_none: If True, only include non-empty values in the response.

        Returns:
            Dict[str, Any]: The dictionary representation of the instance.
        """

    def _remove_none(data: Any) -> Any:
      """Recursively removes None or empty values from a dictionary or list."""
      if isinstance(data, dict):
        return {k: _remove_none(v) for k, v in data.items() if v is not None}
      elif isinstance(data, list):
        return [_remove_none(item) for item in data]
      return data

    result = asdict(self)
    return _remove_none(result) if exclude_none else result

  def to_json(self, exclude_none: bool = True) -> str:
    """Converts the instance to a JSON string.

        Args:
            exclude_none: If True, only include non-empty values in the response.

        Returns:
            str: The JSON string representation of the instance.
        """
    return json.dumps(self.to_dict(exclude_none=exclude_none), indent=2)


def listify(v: Any) -> list[str]:
  if isinstance(v, (str, bytes)):
    return [v]
  if not isinstance(v, Iterable):
    return [v]
  return list(v)


variableDCID: TypeAlias = str
facetID: TypeAlias = str
orderedFacetsLabel: TypeAlias = str

ListOrStr = Annotated[list[str] | str, BeforeValidator(listify)]
