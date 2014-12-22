#!/usr/bin/env python3

import argparse
from distutils.version import LooseVersion
import collections
import subprocess
import sys
import re


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
    args.add_argument('-n', '--new-versions', action='store_true')
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
        package_map[name].append(LooseVersion(version))
    package_list = [(name, versions) for name, versions in package_map.items()]
    package_list.sort(key=lambda x: x[0])
    for _, versions in package_list:
        versions.sort()
    return package_list


def _match_package_information(pkg_text):
    """Match package information for use in get_available_version_list()."""
    def split_and_sort_versions(pkg, name):
        pkg[name] = [LooseVersion(ver) for ver in pkg[name].split(', ')]
        pkg[name].sort()

    pkg_match = {
        'name':      re.compile(r'.\s([a-zA-Z][a-zA-Z-\d]*)'),
        'available': re.compile(r'\s+Default available version: (.*)$'),
        'installed': re.compile(r'\s+Installed versions: (.*)$'),
    }

    pkg = {}
    for line in pkg_text:
        for name, regex in pkg_match.items():
            if name not in pkg:
                try:
                    pkg[name] = regex.match(line).group(1)
                except AttributeError:
                    pass
    split_and_sort_versions(pkg, 'installed')
    split_and_sort_versions(pkg, 'available')
    return pkg


def get_available_version_list():
    cabal_args = ['cabal', 'list', '--installed']
    cabal = subprocess.check_output(cabal_args, universal_newlines=True)
    packages = [pkg.split('\n') for pkg in cabal.strip().split('\n\n')]

    package_info_map = []
    for pkg_text in packages:
        pkg = _match_package_information(pkg_text)
        package_info_map.append(pkg)
    package_info_map.sort(key=lambda x: x['name'])
    print(package_info_map)


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
    if args.installed:
        packages = filter_packages(get_package_list(), args.installed)
    else:
        packages = get_package_list()

    if args.old:
        packages = old(packages)

    if args.new_versions:
        get_available_version_list()
    else:
        display_packages(packages, args.version_separator, args.id)

    # args_parser.print_help()

if __name__ == '__main__':
    main()
