import torch


def verify_checkpoint():
    path = "outputs/models/gatv2_best.pt"
    print(f"Loading checkpoint from: {path}")

    ckpt = torch.load(path, map_location="cpu", weights_only=False)
    print(f"Checkpoint keys: {list(ckpt.keys())}")

    if "architecture" in ckpt:
        print(f"Architecture metadata: {ckpt['architecture']}")
    else:
        print("MISSING 'architecture' key!")


if __name__ == "__main__":
    verify_checkpoint()
