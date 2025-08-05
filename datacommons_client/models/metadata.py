from typing import Optional, TypeAlias

from pydantic import AnyUrl

from datacommons_client.models.base import BaseDCModel
from datacommons_client.models.base import entityDCID
from datacommons_client.models.base import ListLikeRootModel
from datacommons_client.models.base import variableDCID

variableName: TypeAlias = str
entityName: TypeAlias = str
topicDCID: TypeAlias = str
topicName: TypeAlias = str
description: TypeAlias = str
unit: TypeAlias = str
observationPeriod: TypeAlias = str
measurementMethod: TypeAlias = str


class Source(BaseDCModel):
  """Represents a source in the Data Commons knowledge graph.

    Attributes:
        dcid: The unique identifier for the source.
        name: The name of the source.
        url: A description of the source.
        license: The license under which the source is provided.
    """

  dcid: Optional[str]
  name: Optional[str] = None
  url: Optional[AnyUrl] = None
  license: Optional[str] = None


class Topic(BaseDCModel):
  """Represents a topic in the Data Commons knowledge graph.""" ""
  dcid: Optional[topicDCID]
  name: Optional[topicName] = None


class Topics(ListLikeRootModel[Topic]):
  """Represents a list of topics in the Data Commons knowledge graph."""


class Sources(ListLikeRootModel[Source]):
  """Represents a list of sources in the Data Commons knowledge graph."""


class Entity(BaseDCModel):
  """Represents a entity in the Data Commons knowledge graph."""

  dcid: entityDCID
  name: Optional[entityName] = None


class Entities(ListLikeRootModel[Entity]):
  """Represents a list of entities in the Data Commons knowledge graph."""


class Units(ListLikeRootModel[unit]):
  """Represents a list of units in the Data Commons knowledge graph."""


class MeasurementMethods(ListLikeRootModel[measurementMethod]):
  """Represents a list of measurement methods in the Data Commons knowledge graph."""


class ObservationPeriods(ListLikeRootModel[observationPeriod]):
  """Represents a list of observation periods in the Data Commons knowledge graph."""


class DateRange(BaseDCModel):
  """Represents a date range in the Data Commons knowledge graph.

    Attributes:
        start: The start date of the range.
        end: The end date of the range.
    """

  start: Optional[str] = None
  end: Optional[str] = None


class StatVarMetadata(BaseDCModel):
  """Represents metadata for a variable in the Data Commons knowledge graph.

    Attributes:
        dcid: The unique identifier for the variable.
        name: The name of the variable.
        topic: The topic(s) associated with the variable.
        description: A description of the variable.
        source: The source(s) of the variable.
        entity: The entity(ies) associated with the variable.
        dateRange: The date range for the variable.
        unit: The unit of measurement for the variable.
        observationPeriod: The observation period for the variable.
        measurementMethod: The method used to measure the variable.

    """

  dcid: variableDCID
  name: Optional[variableName] = None
  topic: Optional[Topics] = None
  description: Optional[description] = None
  source: Optional[Sources] = None
  entity: Optional[Entities] = None
  dateRange: Optional[DateRange] = None
  unit: Optional[Units] = None
  observationPeriod: Optional[ObservationPeriods] = None
  measurementMethod: Optional[MeasurementMethods] = None
