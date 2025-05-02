import os
import argparse
import sys
import json
from pprint import pprint
from .merge import merge_directory_toml
from warnings import warn

def basedir(kwargs):
    basedir = os.path.expanduser(f"~/.{kwargs['app']}/")
    os.makedirs(basedir, exist_ok=True)
    return basedir

def do_tomlmerge(input_dir, strategy, output, log_file, **kwargs):
    # b = basedir(kwargs)
    conflict_log = []
    merged_data = merge_directory_toml(input_dir, strategy, conflict_log)

    with open(output, 'w', encoding='utf-8') as fout:
        pprint(merged_data, fout, indent=2)

    count = len(glob.glob(os.path.join(input_dir, '*.toml')))
    print(f"Merged {count} TOML files into '{output}' using strategy '{strategy}'.")

    if strategy == 'log':
        if conflict_log:
            if log_file:
                with open(log_file, 'w', encoding='utf-8') as lf:
                    json.dump(conflict_log, lf, indent=2, ensure_ascii=False)
                print(f"Conflict log written to '{log_file}' ({len(conflict_log)} entries).")
            else:
                print(f"Conflict log ({len(conflict_log)} entries):")
                print(json.dumps(conflict_log, indent=2, ensure_ascii=False))
        else:
            print("No conflicts detected.")

def main():
    params = {"app": "tomlmerge"}

    parser = argparse.ArgumentParser(
        prog=params["app"],
        description="Merge all TOML files in a directory with configurable conflict handling.",
        epilog=f'python -m {params["app"]}')

    parser.add_argument('input_dir', help="Directory containing TOML files to merge")
    parser.add_argument('output', help="Output path for merged TOML file")
    parser.add_argument('--strategy', choices=['override','seq','skip','log'], default='seq',
                        help="Conflict strategy: override, seq (uniquify), skip (ignore), log (ignore + record)")
    parser.add_argument('--log-file', help="Path to write JSON conflict log (only for log strategy)")
    args = parser.parse_args()
    params = params | vars(args)

    set_warnigs_hook()
    try:
        do_tomlmerge(**params)
    except Exception as e:
        print(f'{e.__class__.__name__}:', *e.args)
        return 1
    
    return 0

def set_warnigs_hook():
    import sys
    import warnings
    def on_warn(message, category, filename, lineno, file=None, line=None):
        print(f'Warning: {message}', file=sys.stderr)
    warnings.showwarning = on_warn

if __name__ == '__main__':
    sys.exit(main())
