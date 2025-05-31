from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from pydantic import field_validator
from pydantic import model_serializer

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
    message = f"Invalid `select` field: '{value}'. Only {', '.join(cls.valid_values())} are allowed."
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

    missing_fields = required_select - set(select)
    if missing_fields:
      raise ValueError(
          f"The 'select' field must include at least the following: {', '.join(required_select)} "
          f"(missing: {', '.join(missing_fields)})")

    return select

  @model_serializer
  def serialize(self) -> list:
    """Return directly as list"""
    return self.select


@dataclass
class Observation:
  """Represents an observation with a date and value.

    Attributes:
        date (str): The date of the observation.
        value (float): The value of the observation.
    """

  date: str
  value: float

  @classmethod
  def from_json(cls, json_data: Dict[str, Any]) -> "Observation":
    """Creates an Observation instance from the response data.

        Args:
            json_data: A dictionary containing observation data.

        Returns:
            An Observation instance.
        """
    return cls(
        date=json_data.get("date"),
        value=json_data.get("value"),
    )


@dataclass
class OrderedFacets:
  """Represents ordered facets of observations.

    Attributes:
        earliestDate (str): The earliest date in the observations.
        facetId (str): The identifier for the facet.
        latestDate (str): The latest date in the observations.
        obsCount (int): The total number of observations.
        observations (List[Observation]): A list of observations associated with the facet.
    """

  earliestDate: str = field(default_factory=str)
  facetId: str = field(default_factory=str)
  latestDate: str = field(default_factory=str)
  obsCount: int = field(default_factory=int)
  observations: list[Observation] = field(default_factory=list)

  @classmethod
  def from_json(cls, json_data: Dict[str, Any]) -> "OrderedFacets":
    """Creates an OrderedFacets instance from the response data.

        Args:
            json_data (Dict[str, Any]): A dictionary containing ordered facets data.

        Returns:
            OrderedFacets: An instance of the OrderedFacets class.
        """
    return cls(
        earliestDate=json_data.get("earliestDate"),
        facetId=json_data.get("facetId"),
        latestDate=json_data.get("latestDate"),
        obsCount=json_data.get("obsCount"),
        observations=[
            Observation.from_json(observation)
            for observation in json_data.get("observations", [])
        ],
    )


@dataclass
class Variable:
  """Represents a variable with data grouped by entity.

    Attributes:
        byEntity (Dict[str, Dict[orderedFacetsLabel, List[OrderedFacets]]]): A dictionary mapping
            entities to their ordered facets.
    """

  byEntity: Dict[str, Dict[orderedFacetsLabel,
                           list[OrderedFacets]]] = field(default_factory=dict)

  @classmethod
  def from_json(cls, json_data: Dict[str, Any]) -> "Variable":
    """Creates a Variable instance from the response data.

        Args:
            json_data (Dict[str, Any]): A dictionary containing variable data.

        Returns:
            Variable: An instance of the Variable class.
        """
    return cls(
        byEntity={
            entity: {
                "orderedFacets": [
                    OrderedFacets.from_json(facet_data)
                    for facet_data in entity_data.get("orderedFacets", {})
                ]
            } for entity, entity_data in json_data.get("byEntity", {}).items()
        })


@dataclass
class Facet:
  """Represents metadata for a facet.

    Attributes:
        importName (str): The name of the data import.
        measurementMethod (str): The method used to measure the data.
        observationPeriod (str): The period over which the observations were made.
        provenanceUrl (str): The URL of the data's provenance.
        unit (str): The unit of the observations.
    """

  importName: str = field(default_factory=str)
  measurementMethod: str = field(default_factory=str)
  observationPeriod: str = field(default_factory=str)
  provenanceUrl: str = field(default_factory=str)
  unit: str = field(default_factory=str)

  @classmethod
  def from_json(cls, json_data: Dict[str, Any]) -> "Facet":
    """
        Args:
            json_data (Dict[str, Any]): A dictionary containing facet data.

        Returns:
            Facet: An instance of the Facet class.
        """
    return cls(
        importName=json_data.get("importName"),
        measurementMethod=json_data.get("measurementMethod"),
        observationPeriod=json_data.get("observationPeriod"),
        provenanceUrl=json_data.get("provenanceUrl"),
        unit=json_data.get("unit"),
    )
