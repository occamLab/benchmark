import torch
from pathlib import Path


if __name__ == '__main__':
    original = Path("/tmp/benchmark/original-model.pt")
    module_list = Path("/tmp/benchmark/modulelist-model.pt")
    original_dic = torch.load(original, map_location="cpu")
    new_dic = torch.load(module_list, map_location="cpu")

    torch.set_printoptions(threshold=10_000)
    print(original_dic)
