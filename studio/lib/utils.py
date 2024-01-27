import gc
import glob

import multiprocessing

import numpy as np
import psutil
import torch
from lib import get_cwd

torch.manual_seed(1337)
CWD = get_cwd()


def get_filenames(root=CWD, folder="**", exts=None, name_filters=None):
    if name_filters is None:
        name_filters = [""]

    if exts is None:
        exts = ["*"]

    file_names = []

    for ext in exts:
        file_names.extend(glob.glob(f"{root}/{folder}/*.{ext}", recursive=True))

    return sorted(
        [
            ele
            for ele in file_names
            if any([nf.lower() in ele.lower() for nf in name_filters])
        ]
    )


def gc_collect():
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
    elif torch.backends.mps.is_available():
        torch.mps.empty_cache()
    gc.set_threshold(100, 10, 1)
    gc.collect()


def get_optimal_torch_device(index=0) -> torch.device:
    if torch.cuda.is_available():
        return torch.device(f"cuda:{index % torch.cuda.device_count()}")  # Very fast
    elif torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def get_optimal_threads(offset=0):
    cores = multiprocessing.cpu_count() - offset
    return max(np.floor(cores * (1 - psutil.cpu_percent())), 1)
