from typing import Annotated, Any, Dict, Iterable, TypeAlias

from pydantic import BaseModel
from pydantic import BeforeValidator
from pydantic import ConfigDict

variableDCID: TypeAlias = str
facetID: TypeAlias = str
orderedFacetsLabel: TypeAlias = str


def listify(v: Any) -> list[str]:
  if isinstance(v, (str, bytes)):
    return [v]
  if not isinstance(v, Iterable):
    return [v]
  return list(v)


ListOrStr = Annotated[list[str] | str, BeforeValidator(listify)]


class BaseDCModel(BaseModel):
  """Provides serialization methods for the Response dataclasses."""

  model_config = ConfigDict(
      validate_by_name=True,
      validate_default=True,
      validate_by_alias=True,
      use_enum_values=True,
      serialize_by_alias=True,
  )

  @classmethod
  def from_json(cls, json_data: Dict[str, Any]) -> "BaseDCModel":
    return cls.model_validate(json_data)

  def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
    """Converts the instance to a dictionary.

        Args:
            exclude_none: If True, only include non-empty values in the response.

        Returns:
            Dict[str, Any]: The dictionary representation of the instance.
        """

    return self.model_dump(mode="python", exclude_none=exclude_none)

  def to_json(self, exclude_none: bool = True) -> str:
    """Converts the instance to a JSON string.

        Args:
            exclude_none: If True, only include non-empty values in the response.

        Returns:
            str: The JSON string representation of the instance.
        """
    return self.model_dump_json(exclude_none=exclude_none, indent=2)
