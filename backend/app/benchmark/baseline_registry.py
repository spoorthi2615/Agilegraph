import logging
from typing import Dict, Type
from app.benchmark.baseline import Baseline

class BaselineRegistry:
    """
    Singleton registry managing all available baseline implementations.
    Decouples the BenchmarkRunner from direct dependencies on concrete implementations.
    """
    _registry: Dict[str, Type[Baseline]] = {}

    @classmethod
    def register(cls, name: str, baseline_class: Type[Baseline]) -> None:
        """Registers a baseline class under a string identifier."""
        if name in cls._registry:
            logging.warning(f"Baseline {name} is already registered. Overwriting.")
        cls._registry[name] = baseline_class
        logging.info(f"Registered benchmark baseline: {name}")

    @classmethod
    def unregister(cls, name: str) -> None:
        """Removes a baseline from the registry."""
        if name in cls._registry:
            del cls._registry[name]

    @classmethod
    def discover(cls) -> Dict[str, Type[Baseline]]:
        """Returns a safe copy of the registered baselines."""
        return dict(cls._registry)

    @classmethod
    def instantiate(cls, name: str) -> Baseline:
        """Instantiates and returns the requested baseline."""
        if name not in cls._registry:
            raise KeyError(f"Baseline '{name}' not found in registry.")
        return cls._registry[name]()
