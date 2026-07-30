from abc import ABC, abstractmethod
from app.models.crypto_graph import CryptoGraph
from app.models.training_dataset import TrainingDataset
from app.benchmark.benchmark_result import BenchmarkResult

class Baseline(ABC):
    """
    Abstract interface for all baseline prediction strategies.
    Ensures that any statistical or heuristic engine can be swapped effortlessly
    into the BenchmarkRunner.
    """
    @abstractmethod
    def initialize(self) -> None:
        """
        Prepares any heavy resources or static initializations before benchmarking begins.
        """

    @abstractmethod
    def get_name(self) -> str:
        pass
        
    @abstractmethod
    def get_version(self) -> str:
        pass

    @abstractmethod
    def predict(self, dataset: TrainingDataset, graph: CryptoGraph) -> BenchmarkResult:
        """
        Executes the baseline algorithm over the repository and returns structured predictions.
        """
