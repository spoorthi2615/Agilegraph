import pytest
import torch
from app.models.model_config import ModelConfig
from app.models.training_dataset import TrainingDataset
from app.services.gatv2_model_service import GATv2ModelService, TORCH_AVAILABLE
from app.services.feature_engineering_service import FeatureEngineeringService
from app.services.gatv2_evaluation_service import GATv2EvaluationService


@pytest.mark.skipif(not TORCH_AVAILABLE, reason="PyTorch is required for this test")
def test_gatv2_model_initialization_and_forward_pass():
    # 1. Simulate feature engineering output
    # For testing, we mock a structured TrainingDataset rather than running full FeatureEngineeringService
    # since FeatureEngineeringService requires a Neo4j driver connection or an AssetGraph object.

    config = ModelConfig(
        input_dimension=3, hidden_dimension=16, output_dimension=2, attention_heads=2, dropout=0.1
    )

    dataset = TrainingDataset(
        project_id="test_project",
        total_nodes=3,
        total_edges=2,
        node_features=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]],
        edge_index=[(0, 1), (1, 2)],
        node_labels=[0, 1, 0],
        train_mask=[True, True, False],
        val_mask=[False, False, True],
    )

    # 2. Test Model Service Initialization
    model = GATv2ModelService.initialize_model(dataset, config)

    # Ensure it returned a PyTorch nn.Module and not the fallback dictionary
    assert isinstance(model, torch.nn.Module)

    # 3. Test a Forward Pass with real PyTorch Geometric tensors
    # Convert dataset to tensors as the training loop would do
    x = torch.tensor(dataset.node_features, dtype=torch.float)
    # PyTorch Geometric expects edge_index in [2, num_edges] shape
    edge_index = torch.tensor(dataset.edge_index, dtype=torch.long).t().contiguous()

    out = model(x, edge_index)

    # The output should have shape [num_nodes, output_dimension]
    # Because attention_heads is 1 in the second layer of GATv2NodeClassifier
    assert out.shape == (3, 2)
    assert not torch.isnan(out).any(), "Model produced NaN outputs"


from app.models.training_result import TrainingResult


@pytest.mark.skipif(not TORCH_AVAILABLE, reason="PyTorch is required for this test")
def test_evaluation_service_metrics():
    # Test the evaluation service using dummy data
    config = ModelConfig(
        input_dimension=3, hidden_dimension=16, output_dimension=1, attention_heads=2, dropout=0.1
    )

    # We create a dummy dataset where node_labels are 0 or 100 (threshold is 75)
    dataset = TrainingDataset(
        project_id="test_eval",
        total_nodes=4,
        total_edges=2,
        node_features=[[0.1, 0.1, 0.1], [0.2, 0.2, 0.2], [0.3, 0.3, 0.3], [0.4, 0.4, 0.4]],
        edge_index=[(0, 1), (2, 3)],
        node_labels=[0, 100, 0, 100],
    )

    from datetime import datetime, timezone

    training_result = TrainingResult(
        project_id="test_eval",
        model_id=config.model_id,
        dataset_id=dataset.dataset_id,
        final_training_loss=0.5,
        final_validation_loss=0.5,
        training_duration_seconds=1.0,
        training_completed=True,
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
        epochs=10,
        learning_rate=0.01,
        optimizer="Adam",
        loss_history=[],
    )

    model = GATv2ModelService.initialize_model(dataset, config)

    eval_result = GATv2EvaluationService.evaluate_model(training_result, model, dataset, config)

    assert eval_result.evaluation_completed is True
    assert eval_result.accuracy >= 0.0
    assert eval_result.f1_score >= 0.0
