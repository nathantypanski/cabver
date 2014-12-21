#!/usr/bin/env python3

import argparse
from distutils.version import LooseVersion
import collections
import subprocess
import sys


def build_args():
    args = argparse.ArgumentParser()
    args.add_argument('-i', '--installed',
                      help='list installed versions',
                      type=str,
                      nargs='*')
    args.add_argument('-o', '--old',
                      help='Operate only on old versions of packages.'
                           ' for example, when used with --installed,'
                           ' this will list only old versions of installed'
                           ' packages.' ,
                      action='store_true', default=False)
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
                         action='store_true', default=False)
    return args


def get_package_list():
    """Get a list of installed packages and their versions from Cabal.

    The output will be a list of the form [[package, version]].
    """
    cabal_args = ['cabal', 'list', '--installed', '--simple-output']
    cabal = subprocess.check_output(cabal_args, universal_newlines=True)

    package_list = [pkg.split(' ') for pkg in cabal.strip('\n').split('\n')]
    package_map = collections.defaultdict(list)
    for name, version in package_list:
        package_map[name].append(version)
    package_list = [(name, versions) for name, versions in package_map.items()]
    package_list.sort(key=lambda x: x[0])
    return package_list


def display_packages(packages, version_separator=None, id_form=False):
    """Prints to STDOUT a list of package names and their versions.

    Args:
        packages: a list [name, [versions]], where versions will be converted
            into strings before printing, and name is a single string.
    """
    for name, versions in packages:
        if id_form:
            for ver in versions:
                print(name, str(ver), sep='-')
        else:
            print(name, end=' ')
            for ver in versions[:-1]:
                print(str(ver), end=version_separator)
            print(versions[-1])


def old(packages):
    """Convert a collated list of packages into a list of only old packages."""
    old_packages = []
    for name, versions in packages:
        if len(versions) > 1:
            old_packages.append((name, versions[:-1]))
    return old_packages


def filter_packages(packages, names):
    """Filter the packages to only those ones contained in names."""
    names = set(names)
    return [(pkg, ver) for pkg, ver in packages if pkg in names]


def validate_args(args):
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
    validate_args(args)
    if args.installed is not None:
        if args.installed:
            packages = filter_packages(get_package_list(), args.installed)
        else:
            packages = get_package_list()

        if args.old:
            packages = old(packages)

        display_packages(packages, args.version_separator, args.id)

    else:
        args_parser.print_help()

if __name__ == '__main__':
    main()
