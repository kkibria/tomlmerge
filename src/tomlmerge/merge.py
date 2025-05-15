import tomllib
import glob
import os

def merge_dicts(d1: dict, d2: dict, strategy: str, conflicts: list, path: str = '') -> dict:
    """
    Recursively merge d2 into d1 with a given conflict strategy.
    - "override": later values replace earlier ones.
    - "seq": later values are added under a new key with a sequential suffix.
    - "skip": conflicting later values are ignored.
    - "log": conflicting later values are ignored but logged.

    Lists under the same key are concatenated without duplicates.
    Dicts are merged recursively.
    """
    merged = d1.copy()
    for key, val in d2.items():
        full_key = f"{path}.{key}" if path else key
        if key in merged:
            # Both dicts -> recurse
            if isinstance(merged[key], dict) and isinstance(val, dict):
                merged[key] = merge_dicts(merged[key], val, strategy, conflicts, full_key)
            # Both lists -> join unique
            elif isinstance(merged[key], list) and isinstance(val, list):
                existing = merged[key]
                merged[key] = existing + [x for x in val if x not in existing]
            else:
                # Scalar or mismatched types -> conflict resolution
                if strategy == 'override':
                    merged[key] = val
                elif strategy == 'seq':
                    i = 1
                    new_key = f"{key}_{i}"
                    while new_key in merged:
                        i += 1
                        new_key = f"{key}_{i}"
                    merged[new_key] = val
                elif strategy == 'skip':
                    pass  # keep the original merged[key]
                elif strategy == 'log':
                    conflicts.append({
                        'key': full_key,
                        'existing': merged[key],
                        'new': val
                    })
                else:
                    raise ValueError(f"Unknown strategy: {strategy}")
        else:
            merged[key] = val
    return merged


# strategy values: 'override','seq','skip','log'
def merge_directory_toml(input_dir: str, strategy: str, conflicts: list) -> dict:
    """
    Merge all .toml files in input_dir (sorted) using merge_dicts.
    """
    pattern = os.path.join(input_dir, '*.toml')
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No TOML files found in directory: {input_dir}")
    merged = {}
    for toml_file in files:
        with open(toml_file, 'rb') as f:
            print(f"loading {toml_file}...")
            data = tomllib.load(f)
        merged = merge_dicts(merged, data, strategy, conflicts)
    return merged

