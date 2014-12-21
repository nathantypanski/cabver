#!/usr/bin/env python3

import subprocess
import argparse
import collections
from distutils.version import LooseVersion
import re
import sys

def build_args():
    args = argparse.ArgumentParser()
    args.add_argument('-l', '--list', metavar='NAME', nargs='*')
    display = args.add_argument_group('display options')
    display.add_argument('--version-separator',
                         help='separate version numbers with SEP.'
                              ' defaults to " "'
                              ' mutually exclusive with --id.',
                         metavar='SEP', default=' ')
    display.add_argument('--id',
                         help='display a ghc-pkg compatible id'
                              ' for each package.'
                              ' e.g., Cabal-1.20.0.3',
                         action='store_true')
    return args

def get_package_list():
    pkg = subprocess.Popen(['ghc-pkg', 'list', '--user'], stdout=subprocess.PIPE, universal_newlines=True)
    stdout, stderr = pkg.communicate()
    packages = collections.defaultdict(list)
    lines = [line.strip() for line in stdout.split('\n') if line.startswith(' ')]
    for package in lines:
        package_parser = re.compile('([a-zA-Z][a-zA-Z-\d]*)-(\d+(\.\d+)+)')
        match = package_parser.match(package)
        if match:
            name = match.group(1)
            ver = match.group(2)
            packages[name].append(LooseVersion(ver))
        else:
            print('Failed to parse: {}'.format(package), file=sys.stderr)
    packages = [(name, versions) for name, versions in packages.items()]
    for name, versions in packages:
        versions.sort()
    packages.sort()
    return packages

def display_packages(packages, version_separator):
    for name, versions in packages:
        print(name, end=' ')
        for ver in versions[:-1]:
            print(str(ver), end=version_separator)
        print(versions[-1])

def validate_args(args, args_parser):
    """Validate that no mutually exclusive arguments have been passed.

    This is needed since argparse.ArgumentParser won't let you put mutually
    exclusive args in an argument group.
    """
    if args.id and args.version_separator != ' ':
        print("You can't use --version-separator with --id.", file=sys.stderr)
        exit(1)

def main():
    args_parser = build_args()
    args = args_parser.parse_args()
    packages = get_package_list()
    validate_args(args, args_parser)
    if args.list == []:
        display_packages(packages,
                         version_separator=args.version_separator)
    elif args.list:
        for package in args.list:
            display_packages(packages[package],
                             version_separator=args.version_separator)
    else:
        args_parser.print_help()

if __name__ == '__main__':
    main()
