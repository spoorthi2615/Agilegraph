import subprocess
import sys


def test_semgrep():
    print("Testing Semgrep subprocess...")
    try:
        result = subprocess.run(
            ["semgrep", "--version"], capture_output=True, text=True, check=True
        )
        print(f"Semgrep successfully invoked: {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"Failed to run Semgrep: {e}")
        return False


def test_transformers():
    print("\nTesting Transformers loading...")
    try:
        import transformers

        print(f"Transformers successfully imported. Version: {transformers.__version__}")
        return True
    except Exception as e:
        print(f"Failed to load Transformers: {e}")
        return False


def test_gatv2():
    print("\nTesting GATv2 forward pass...")
    try:
        import torch
        from torch_geometric.nn import GATv2Conv

        in_channels = 16
        out_channels = 8
        heads = 2

        conv = GATv2Conv(in_channels, out_channels, heads=heads)

        # Create dummy graph
        x = torch.randn(4, in_channels)  # 4 nodes
        edge_index = torch.tensor([[0, 1, 1, 2, 2, 3], [1, 0, 2, 1, 3, 2]], dtype=torch.long)

        out = conv(x, edge_index)

        expected_shape = (4, out_channels * heads)
        if out.shape == expected_shape:
            print(f"GATv2 forward pass successful! Output shape: {out.shape}")
            return True
        else:
            print(f"GATv2 output shape mismatch: {out.shape} != {expected_shape}")
            return False

    except Exception as e:
        print(f"Failed GATv2 test: {e}")
        return False


if __name__ == "__main__":
    s = test_semgrep()
    t = test_transformers()
    g = test_gatv2()

    if s and t and g:
        print("\nAll ML diagnostics PASSED!")
        sys.exit(0)
    else:
        print("\nSome ML diagnostics FAILED!")
        sys.exit(1)
