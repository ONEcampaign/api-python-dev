from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator
from pydantic import model_serializer

from datacommons_client.models.base import BaseDCModel
from datacommons_client.models.base import orderedFacetsLabel
from datacommons_client.utils.error_handling import InvalidObservationSelectError


class ObservationDate(str, Enum):
  LATEST = "LATEST"
  ALL = ""

  @classmethod
  def _missing_(cls, value):
    if isinstance(value, str):
      u = value.strip().upper()
      if u == "LATEST":
        return cls.LATEST
      if u in ("ALL", ""):
        return cls.ALL
    raise ValueError(f"Invalid date value: '{value}'. Only 'LATEST' or"
                     f" '' (empty string) are allowed.")


class ObservationSelect(str, Enum):
  DATE = "date"
  VARIABLE = "variable"
  ENTITY = "entity"
  VALUE = "value"
  FACET = "facet"

  @classmethod
  def valid_values(cls):
    """Returns a list of valid enum values."""
    return sorted(cls._value2member_map_.keys())

  @classmethod
  def _missing_(cls, value):
    """Handle missing enum values by raising a custom error."""
    message = f"Invalid `select` Field: '{value}'. Only {', '.join(cls.valid_values())} are allowed."
    raise InvalidObservationSelectError(message=message)


class ObservationSelectList(BaseModel):
  """A model to represent a list of ObservationSelect values.

    Attributes:
        select (List[ObservationSelect]): A list of ObservationSelect enum values.
    """

  select: Optional[List[ObservationSelect | str]] = None

  @field_validator("select", mode="before")
  def _validate_select(cls, v):
    if v is None:
      select = [
          ObservationSelect.DATE,
          ObservationSelect.VARIABLE,
          ObservationSelect.ENTITY,
          ObservationSelect.VALUE,
      ]
    else:
      select = v

    select = [ObservationSelect(s).value for s in select]

    required_select = {"variable", "entity"}

    missing_Fields = required_select - set(select)
    if missing_Fields:
      raise ValueError(
          f"The 'select' Field must include at least the following: {', '.join(required_select)} "
          f"(missing: {', '.join(missing_Fields)})")

    return select

  @model_serializer
  def serialize(self) -> list:
    """Return directly as list"""
    return self.select


class Observation(BaseDCModel):
  """Represents an observation with a date and value.

    Attributes:
        date (str): The date of the observation.
        value (float): Optional. The value of the observation.
    """

  date: str
  value: Optional[float] = Field(default=None)


class OrderedFacets(BaseDCModel):
  """Represents ordered facets of observations.

    Attributes:
        earliestDate (str): The earliest date in the observations.
        facetId (str): The identifier for the facet.
        latestDate (str): The latest date in the observations.
        obsCount (int): The total number of observations.
        observations (List[Observation]): A list of observations associated with the facet.
    """

  earliestDate: Optional[str] = Field(default=None)
  facetId: Optional[str] = Field(default=None)
  latestDate: Optional[str] = Field(default=None)
  obsCount: Optional[int] = Field(default=None)
  observations: list[Observation] = Field(default_factory=list)


class Variable(BaseDCModel):
  """Represents a variable with data grouped by entity.

    Attributes:
        byEntity (Dict[str, Dict[orderedFacetsLabel, List[OrderedFacets]]]): A dictionary mapping
            entities to their ordered facets.
    """

  byEntity: Dict[str, Dict[orderedFacetsLabel,
                           list[OrderedFacets]]] = Field(default_factory=dict)


class Facet(BaseDCModel):
  """Represents metadata for a facet.

    Attributes:
        importName (str): The name of the data import.
        measurementMethod (str): The method used to measure the data.
        observationPeriod (str): The period over which the observations were made.
        provenanceUrl (str): The URL of the data's provenance.
        unit (str): The unit of the observations.
    """

  importName: Optional[str] = Field(default=None)
  measurementMethod: Optional[str] = Field(default=None)
  observationPeriod: Optional[str] = Field(default=None)
  provenanceUrl: Optional[str] = Field(default=None)
  unit: Optional[str] = Field(default=None)
