#!/usr/bin/env python3

import argparse
from distutils.version import LooseVersion
import subprocess
import sys
import re


def build_args():
    args = argparse.ArgumentParser()
    args.add_argument('-i', '--installed',
                      help='list installed versions',
                      type=str,
                      nargs='*')
    args.add_argument('-m', '--multiple',
                      help='Display packages with multiple versions installed.',
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


def _match_package_information(pkg_text):
    """Match package information for use in get_available_version_list()."""

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

    pkg['installed'] = [LooseVersion(ver) for ver in pkg['installed'].split(', ')]
    pkg['installed'].sort()
    pkg['available'] = LooseVersion(pkg['available'])
    return pkg


def get_package_list():
    """Get a list of packages from Cabal."""
    cabal_args = ['cabal', 'list', '--installed']
    cabal = subprocess.check_output(cabal_args, universal_newlines=True)
    packages = [pkg.split('\n') for pkg in cabal.strip().split('\n\n')]

    package_info_map = []
    for pkg_text in packages:
        pkg = _match_package_information(pkg_text)
        package_info_map.append(pkg)
    package_info_map.sort(key=lambda x: x['name'])
    return package_info_map


def display_packages(packages,
                     version_separator=None,
                     id_form=False,
                     show_available=False):
    """Prints to STDOUT a list of package names and their versions.

    Args:
        packages: a list [name, [versions]], where versions will be converted
            into strings before printing, and name is a single string.
    """
    if version_separator is None:
        version_separator = ', '
    for pkg in packages:
        if id_form and not show_available:
            for ver in pkg['installed']:
                print(pkg['name'], str(ver), sep='-')
        elif id_form:
            print(pkg['name'], str(pkg['available']), sep='-')
        else:
            installed = version_separator.join(
                [str(v) for v in pkg['installed']]
            )
            if show_available:
                print('{}: {} -> {}'.format(pkg['name'],
                                            installed,
                                            pkg['available']))
            else:
                print('{}: {}'.format(pkg['name'], installed))


def has_newer_version(pkg):
    """If pkg has a newer version available, return that version number."""
    latest = pkg['available']
    installed = pkg['installed'][-1]
    try:
        if installed < latest:
            return pkg['available']
    except TypeError:
        # bad version string
        # (e.g., "Not available from any configured repository")
        return False


def filter_new_available(packages):
    """Return only those packages which have newer versions available."""
    return [pkg for pkg in packages if has_newer_version(pkg)]


def filter_multiple_installed(packages):
    """Get those packages with more than one installed version."""
    return [pkg for pkg in packages if len(pkg['installed']) > 1]


def filter_by_names(packages, names):
    """Filter the packages to only those ones contained in names."""
    return [pkg for pkg in packages if pkg['name'] in set(names)]


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
        packages = filter_by_names(get_package_list(), args.installed)
    else:
        packages = get_package_list()

    if args.multiple:
        packages = filter_multiple_installed(packages)

    if args.new_versions:
        packages = filter_new_available(packages)

    display_packages(packages, args.version_separator, args.id, args.new_versions)

    # args_parser.print_help()

if __name__ == '__main__':
    main()
