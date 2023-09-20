#!/usr/bin/env python
import argparse
import json
import os
import subprocess
import sys
from typing import Optional, List

CONFIG_DIR = os.path.join(os.path.expanduser('~'), ".psearch")


def search_for_pattern(
        patterns: List[str],
        path: str,
        include: Optional[str] = None,
        exclude: Optional[str] = None,
        case_sensitive: Optional[bool] = None,
        not_match: Optional[bool] = None,
        silent: Optional[bool] = None
):
    childitem_cmd = [
        'Get-ChildItem',
        '-Path',
        f'"{path}"',
        '-Recurse'
    ]
    if include is not None:
        childitem_cmd.extend(['-Include', f'"{include}"'])
    if exclude is not None:
        childitem_cmd.extend(['-Exclude', f'"{exclude}"'])
    patterns = ", ".join([f"'{pattern}'" for pattern in [pattern.replace("'", "''") for pattern in patterns]])

    select_string_cmd = [
        'Select-String',
        '-Pattern',
        patterns
    ]
    if case_sensitive:
        select_string_cmd.extend(['-CaseSensitive'])
    if not_match:
        select_string_cmd.extend(['-NotMatch'])

    powershell_cmd = f'{" ".join(childitem_cmd)} | {" ".join(select_string_cmd)}'
    if silent:
        powershell_cmd += " | ForEach-Object { $_.Line } | Sort-Object -Unique"
    sp = subprocess.Popen(['powershell', '-command', powershell_cmd], stdout=sys.stdout, stderr=sys.stderr)
    sp.wait()


def list_patterns(configs_dir):
    pattern_files = os.listdir(configs_dir)
    for pattern_file in pattern_files:
        print(pattern_file.rsplit('.', maxsplit=1)[0])


def main():
    parser = argparse.ArgumentParser(description="Search for patterns in files and directories using PowerShell.")
    parser.add_argument("-d", "--dir", default=os.getcwd(), help="Root directory to start the search (default: current directory).")
    parser.add_argument("-p", "--pattern", help="The pattern to search for.")
    parser.add_argument("-l", "--list", action="store_true", help="List all patterns present in the configs directory.")
    parser.add_argument("-s", "--silent", action="store_true", help="Print only matched lines.")
    parser.add_argument("name", nargs='?', help="The name of the pattern file to read from configs directory.")

    args = parser.parse_args()

    if args.list:
        list_patterns(CONFIG_DIR)
    elif args.pattern:
        search_for_pattern([args.pattern], args.dir)
    elif args.name:
        pattern_file_path = os.path.join(CONFIG_DIR, f'{args.name}.json')
        if os.path.exists(pattern_file_path):
            with open(pattern_file_path, "r") as pattern_file:
                pattern = pattern_file.read()
                pattern = json.loads(pattern)
                include = pattern['include'] if 'include' in pattern else None
                exclude = pattern['exclude'] if 'exclude' in pattern else None
                case_sensitive = pattern['case_sensitive'] if 'case_sensitive' in pattern else None
                not_match = pattern['not_match'] if 'not_match' in pattern else None
                if 'pattern' in pattern:
                    patterns = [pattern['pattern']]
                else:
                    patterns = pattern['patterns']
                search_for_pattern(patterns, args.dir, include, exclude, case_sensitive, not_match, args.silent)
        else:
            print(f"Pattern '{args.name}' not found.", file=sys.stderr)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
