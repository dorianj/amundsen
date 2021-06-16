import logging
from typing import Any, Dict, Generator, List, Type, TypeVar

LOGGER = logging.getLogger(__name__)

SCG = TypeVar('SCG', bound='StemmaConfGenerator')


class StemmaConfGenerator(object):
    """
    A generic class for allowing hierarchical configuration to be managed as code,
    producing a flat key value structure suitable for output as environment variables
    or a nested dictionary structure for YAML serialization.


    Env:
        - Produces a list of dictionaries with key/value pairs.
        - Any member not starting with an underscore(_) as long as it's not a list
          is subject to serialization.
        - Members holding StemmaConfGenerator instances are flattened and merged.

    Yaml:
        - Produces an arbitrary nested hashmap.
        - Any member not starting with an underscore(_) is subject to serialization.
        - Members holding StemmaConfGenerator instances are recursively constructed at
          the respective position.
    """

    _logger = LOGGER

    def __init__(self, **kwargs) -> None:  # type: ignore
        existing_attributes = dir(self)
        for kw, val in kwargs.items():
            if kw in existing_attributes:
                setattr(self, kw, val)
            else:
                raise Exception(
                    "Keyword value provided: %s does not exist for config class: %s"
                    % (kw, self)
                )

    @classmethod
    def _is_conf_item(cls: Type[SCG], item: str) -> bool:
        """
        Validate if a field is subject to environment/yaml serialization.
        """
        return not item.startswith("_") and not callable(getattr(cls, item))

    @classmethod
    def _flatten(cls: Type[SCG], coll: List[Any]) -> Generator[Any, None, None]:
        """
        Recursive list flatten.
        """
        for i in coll:
            if isinstance(i, list):
                yield from cls._flatten(i)
            else:
                yield i

    def build_env(self) -> List[Dict[str, Any]]:
        """
        build_env serializes a configuration as a single level flat environment array of .
        Nested configurations are flattened to top level.
        """
        env = []
        for conf in filter(lambda i: self._is_conf_item(i), dir(self)):
            v = getattr(self, conf)

            # Allow using None as default to skip generation
            if v is not None:

                encoded_value: Any = None
                if isinstance(v, StemmaConfGenerator):
                    encoded_value = v.build_env()
                elif not isinstance(v, list):
                    encoded_value = str(v)

                # Allow skipping collections
                if encoded_value is not None:
                    if isinstance(encoded_value, list):
                        env.extend(list(StemmaConfGenerator._flatten(encoded_value)))
                    else:
                        env.append({"key": conf, "value": encoded_value})
        return env

    def build_yaml(self) -> Dict[str, Any]:
        """
        Creates a hashmap matching class representation and ready for serialization.

        """
        yaml: Dict[str, Any] = {}
        for conf in filter(lambda i: self._is_conf_item(i), dir(self)):
            v = getattr(self, conf)
            if v is not None:
                if isinstance(v, StemmaConfGenerator):
                    yaml[conf] = v.build_yaml()
                elif isinstance(v, list):
                    yaml[conf] = [
                        i.build_yaml() if isinstance(i, StemmaConfGenerator) else i
                        for i in v
                    ]
                elif isinstance(v, bool):
                    yaml[conf] = v
                else:
                    yaml[conf] = str(v)
        return yaml
