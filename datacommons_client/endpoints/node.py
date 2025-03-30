from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from datacommons_client.endpoints.base import API
from datacommons_client.endpoints.base import Endpoint
from datacommons_client.endpoints.payloads import NodeRequestPayload
from datacommons_client.endpoints.payloads import normalize_properties_to_string
from datacommons_client.endpoints.response import NodeResponse
from datacommons_client.models.node import Node
from datacommons_client.utils.graph import build_ancestry_map
from datacommons_client.utils.graph import build_ancestry_tree
from datacommons_client.utils.graph import fetch_parents_lru
from datacommons_client.utils.graph import flatten_ancestry
from datacommons_client.utils.graph import Parent

MAX_WORKERS = 20


def _extract_name_from_english_name_property(properties: list | Node) -> str:
  """
    Extracts the name from a list of properties with English names.
    Args:
        properties (list): A list of properties with English names.

    Returns:
        str: The extracted name.
    """
  if isinstance(properties, Node):
    properties = [properties]

  return properties[0].value


def _extract_name_from_property_with_language(
    properties: list, language: str, fallback_to_en: bool) -> Optional[str]:
  """
    Extracts the name from a list of properties with language tags.
    Args:
        properties (list): A list of properties with language tags.
        language (str): The desired language code.
        fallback_to_en (bool): Whether to fall back to English if the desired language is not found.
    """
  # If a non-English language is requested, unpack the response to get it.
  fallback_name = None

  # Iterate through the properties to find the name in the specified language
  for candidate in properties:
    # If no language is specified, skip the candidate
    if "@" not in candidate.value:
      continue

    # Split the candidate value into name and language
    name, lang = candidate.value.rsplit("@", 1)

    # If the language matches, add the name to the dictionary.
    if lang == language:
      return name
    # If language is 'en', store the name as a fallback
    if lang == "en":
      fallback_name = name

  # If no name was found in the specified language, use the fallback name (if available and
  # fallback_to_en is True)
  return fallback_name if fallback_to_en else None


class NodeEndpoint(Endpoint):
  """Initializes the NodeEndpoint with a given API configuration.

    Args:
        api (API): The API instance providing the environment configuration
            (base URL, headers, authentication) to be used for requests.
    """

  def __init__(self, api: API):
    """Initializes the NodeEndpoint with a given API configuration."""
    super().__init__(endpoint="node", api=api)

  def fetch(
      self,
      node_dcids: str | list[str],
      expression: str,
      *,
      all_pages: bool = True,
      next_token: Optional[str] = None,
  ) -> NodeResponse:
    """Fetches properties or arcs for given nodes and properties.

        Args:
            node_dcids (str | List[str]): The DCID(s) of the nodes to query.
            expression (str): The property or relation expression(s) to query.
            all_pages: If True, fetch all pages of the response. If False, fetch only the first page.
              Defaults to True. Set to False to only fetch the first page. In that case, a
              `next_token` key in the response will indicate if more pages are available.
              That token can be used to fetch the next page.
            next_token: Optionally, the token to fetch the next page of results. Defaults to None.

        Returns:
            NodeResponse: The response object containing the queried data.

        Example:
            ```python
            response = node.fetch(
                node_dcids=["geoId/06"],
                expression="<-"
            )
            print(response)
            ```
        """

    # Create the payload
    payload = NodeRequestPayload(node_dcids=node_dcids,
                                 expression=expression).to_dict

    # Make the request and return the response.
    return NodeResponse.from_json(
        self.post(payload, all_pages=all_pages, next_token=next_token))

  def fetch_property_labels(
      self,
      node_dcids: str | list[str],
      out: bool = True,
      *,
      all_pages: bool = True,
      next_token: Optional[str] = None,
  ) -> NodeResponse:
    """Fetches all property labels for the given nodes.

        Args:
            node_dcids (str | list[str]): The DCID(s) of the nodes to query.
            out (bool): Whether to fetch outgoing properties (`->`). Defaults to True.
            all_pages: If True, fetch all pages of the response. If False, fetch only the first page.
              Defaults to True. Set to False to only fetch the first page. In that case, a
              `next_token` key in the response will indicate if more pages are available.
              That token can be used to fetch the next page.
            next_token: Optionally, the token to fetch the next page of results. Defaults to None.

        Returns:
            NodeResponse: The response object containing the property labels.

        Example:
            ```python
            response = node.fetch_property_labels(node_dcids="geoId/06")
            print(response)
            ```
        """
    # Determine the direction of the properties.
    expression = "->" if out else "<-"

    # Make the request and return the response.
    return self.fetch(
        node_dcids=node_dcids,
        expression=expression,
        all_pages=all_pages,
        next_token=next_token,
    )

  def fetch_property_values(
      self,
      node_dcids: str | list[str],
      properties: str | list[str],
      constraints: Optional[str] = None,
      out: bool = True,
      *,
      all_pages: bool = True,
      next_token: Optional[str] = None,
  ) -> NodeResponse:
    """Fetches the values of specific properties for given nodes.

        Args:
            node_dcids (str | List[str]): The DCID(s) of the nodes to query.
            properties (str | List[str]): The property or relation expression(s) to query.
            constraints (Optional[str]): Additional constraints for the query. Defaults to None.
            out (bool): Whether to fetch outgoing properties. Defaults to True.
            all_pages: If True, fetch all pages of the response. If False, fetch only the first page.
              Defaults to True. Set to False to only fetch the first page. In that case, a
              `next_token` key in the response will indicate if more pages are available.
              That token can be used to fetch the next page.
            next_token: Optionally, the token to fetch the next page of results. Defaults to None.


        Returns:
            NodeResponse: The response object containing the property values.

        Example:
            ```python
            response = node.fetch_property_values(
                node_dcids=["geoId/06"],
                properties="name",
                out=True
            )
            print(response)
            ```
        """

    # Normalize the input to a string (if it's a list), otherwise use the string as is.
    properties = normalize_properties_to_string(properties)

    # Construct the expression based on the direction and constraints.
    direction = "->" if out else "<-"
    expression = f"{direction}{properties}"
    if constraints:
      expression += f"{{{constraints}}}"

    return self.fetch(
        node_dcids=node_dcids,
        expression=expression,
        all_pages=all_pages,
        next_token=next_token,
    )

  def fetch_all_classes(
      self,
      *,
      all_pages: bool = True,
      next_token: Optional[str] = None,
  ) -> NodeResponse:
    """Fetches all Classes available in the Data Commons knowledge graph.

        Args:
          all_pages: If True, fetch all pages of the response. If False, fetch only the first page.
              Defaults to True. Set to False to only fetch the first page. In that case, a
              `next_token` key in the response will indicate if more pages are available.
              That token can be used to fetch the next page.
          next_token: Optionally, the token to fetch the next page of results. Defaults to None.


        Returns:
            NodeResponse: The response object containing all statistical variables.

        Example:
            ```python
            response = node.fetch_all_classes()
            print(response)
            ```
        """

    return self.fetch_property_values(
        node_dcids="Class",
        properties="typeOf",
        out=False,
        all_pages=all_pages,
        next_token=next_token,
    )

  def fetch_entity_names(
      self,
      entity_dcids: str | list[str],
      language: Optional[str] = "en",
      fallback_to_en: bool = False,
  ) -> dict[str, str]:
    """
        Fetches entity names in the specified language, with optional fallback to English.

        Args:
          entity_dcids: A single DCID or a list of DCIDs to fetch names for.
          language: Language code (e.g., "en", "es"). Defaults to "en".
          fallback_to_en: If True, falls back to English if the desired language is not found.
            Defaults to False.

        Returns:
          A dictionary mapping each DCID to its name (in the requested or fallback language).
        """

    # Check if entity_dcids is a single string. If so, convert it to a list.
    if isinstance(entity_dcids, str):
      entity_dcids = [entity_dcids]

    # If langauge is English, use the more efficient 'name' property.
    name_property = "name" if language == "en" else "nameWithLanguage"

    # Fetch names the given entity DCIDs.
    data = self.fetch_property_values(
        node_dcids=entity_dcids, properties=name_property).get_properties()

    names: dict[str, str] = {}

    # Iterate through the fetched data and populate the names dictionary.
    for dcid, properties in data.items():
      if language == "en":
        name = _extract_name_from_english_name_property(properties=properties)
      else:
        name = _extract_name_from_property_with_language(
            properties=properties,
            language=language,
            fallback_to_en=fallback_to_en,
        )
      if name:
        names[dcid] = name

    return names

  def fetch_entity_parents(
      self, entity_dcids: str | list[str]) -> dict[str, list[dict[str, str]]]:
    """Fetches the direct parents of one or more entities using the 'containedInPlace' property.

        Args:
            entity_dcids (str | list[str]): A single DCID or a list of DCIDs to query.

        Returns:
            dict[str, list[dict[str, str]]]: A dictionary mapping each input DCID to a list of its
            immediate parent entities. Each parent entity is represented as a dictionary with keys:
            'dcid', 'name', and 'type'.
        """
    if isinstance(entity_dcids, str):
      entity_dcids = [entity_dcids]

    # Fetch property values from the API
    data = self.fetch_property_values(
        node_dcids=entity_dcids,
        properties="containedInPlace",
    ).get_properties()

    result: dict[str, list[dict[str, str]]] = {}

    for entity, properties in data.items():
      if not isinstance(properties, list):
        properties = [properties]

      for parent in properties:
        parent_type = (parent.types[0]
                       if len(parent.types) == 1 else parent.types)
        result.setdefault(entity, []).append({
            "dcid": parent.dcid,
            "name": parent.name,
            "type": parent_type,
        })

    return result

  def _fetch_parents_cached(self, dcid: str) -> tuple[Parent, ...]:
    """Returns cached parent nodes for a given entity using an LRU cache.

        This private wrapper exists because `@lru_cache` cannot be applied directly
        to instance methods. By passing the `NodeEndpoint` instance (`self`) as an
        argument caching is preserved while keeping the implementation modular and testable.

        Args:
            dcid (str): The DCID of the entity whose parents should be fetched.

        Returns:
            tuple[Parent, ...]: A tuple of Parent objects representing the entity's immediate parents.
        """
    return fetch_parents_lru(self, dcid)

  def fetch_entity_ancestry(
      self,
      entity_dcids: str | list[str],
      as_tree: bool = False) -> dict[str, list[dict[str, str]] | dict]:
    """Fetches the full ancestry (flat or nested) for one or more entities.

        For each input DCID, this method builds the complete ancestry graph using a
        breadth-first traversal and parallel fetching.

        It returns either a flat list of unique parents or a nested tree structure for
        each entity, depending on the `as_tree` flag. The flat list matches the structure
        of the `/api/place/parent` endpoint of the DC website.

        Args:
            entity_dcids (str | list[str]): One or more DCIDs of the entities whose ancestry
               will be fetched.
            as_tree (bool): If True, returns a nested tree structure; otherwise, returns a flat list.
                Defaults to False.

        Returns:
            dict[str, list[dict[str, str]] | dict]: A dictionary mapping each input DCID to either:
                - A flat list of parent dictionaries (if `as_tree` is False), or
                - A nested ancestry tree (if `as_tree` is True). Each parent is represented by
                  a dict with 'dcid', 'name', and 'type'.
        """

    if isinstance(entity_dcids, str):
      entity_dcids = [entity_dcids]

    result = {}

    # Use a thread pool to fetch ancestry graphs in parallel for each input entity
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
      futures = [
          executor.submit(
              build_ancestry_map,
              dcid,
              self._fetch_parents_cached,
              max_workers=MAX_WORKERS,
          ) for dcid in entity_dcids
      ]

      # Gather ancestry maps and postprocess into flat or nested form
      for future in futures:
        dcid, ancestry = future.result()
        if as_tree:
          ancestry = build_ancestry_tree(dcid, ancestry)
        else:
          ancestry = flatten_ancestry(ancestry)
        result[dcid] = ancestry

    return result
