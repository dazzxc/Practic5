from pathlib import Path


datasets: dict[str, dict] = {}


def register_dataset(
    dataset_id: str,
    file_path: Path,
    file_name: str,
    file_type: str
):
    datasets[dataset_id] = {
        "file_path": file_path,
        "file_name": file_name,
        "file_type": file_type
    }


def get_dataset(dataset_id: str):
    return datasets.get(dataset_id)
