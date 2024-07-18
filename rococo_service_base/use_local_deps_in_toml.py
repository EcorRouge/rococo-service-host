import argparse
import os
import re
import sys
import textwrap
from argparse import ArgumentParser, Namespace
from os import path
from re import Pattern
from tomlkit import nl, comment, table, items, toml_file, TOMLDocument, item, value
from tomlkit.items import Table
from typing import AnyStr

DEV_PACKAGES_DIR_NAME = 'dev_packages'
ENVS_WITH_DEV_DEPS = ['development', 'local']
DESCRIPTION = f'''\
    This replaces non-path poetry dependencies found in the pyproject.toml file
    with the matching path dependencies from the {DEV_PACKAGES_DIR_NAME}.
    Supported environments: {", ".join(ENVS_WITH_DEV_DEPS)}

    Examples:
        python ./{path.basename(__file__)} ./pyproject.toml

        python ./%(prog)s -h
    '''


def main():

    env = os.environ.get('ENVIRONMENT', '').lower()
    if env not in ENVS_WITH_DEV_DEPS:
        print(f'Skipping execution of {path.basename(__file__)}'
              f'since it is meant for environments: {", ".join(ENVS_WITH_DEV_DEPS)}'
              f'\nThe current environment is: {env}')
        return

    args = parse_commandline_args()
    toml = read_toml_file(args.toml_path)

    dev_packages_dir = path.join(path.dirname(path.abspath(args.toml_path)), DEV_PACKAGES_DIR_NAME)
    if not path.isdir(dev_packages_dir):
        print(f'No development dependencies to replace in the {path.abspath(args.toml_path)} ' 
              f'\nSearched in {dev_packages_dir}')
        return

    replaced_lines: list[items.Comment] = []
    deps: items.Table = get_poetry_table(toml).get('dependencies')
    if deps is not None:
        for k in deps.copy().keys():
            val = deps.get(k)
            if isinstance(val, items.String):
                # handle named dependency
                if replace_dependency_if_matched(k, deps, dev_packages_dir):
                    replaced_lines.append(comment(f'{k} = {val.as_string()}'))
            else:
                # handle path dependency
                if not path.isfile(val.get('path', '')):
                    # this is unavailable path dependency - replace if matched
                    if replace_dependency_if_matched(k, deps, dev_packages_dir):
                        replaced_lines.append(comment(f'{k} = {val.as_string()}'))

    if len(replaced_lines) > 0:
        deps.add(comment('The below dependencies were replaced with the local path dependencies:'))
        for c in replaced_lines:
            deps.add(c)
        deps.add(nl())

        write_toml_file(args.toml_path, toml)
    else:
        print(f'No matching dependencies to replace in the {path.abspath(args.toml_path)} '
              f'\nSearched in {path.abspath(dev_packages_dir)}')


def replace_dependency_if_matched(dep_key: str, deps: Table, dev_packages_dir: str) -> bool:
    src_pkg = get_freshest_pkg_path(dev_packages_dir, dep_key.replace('-', '_'))
    if src_pkg:
        src_pkg_relpath = path.relpath(src_pkg, path.dirname(dev_packages_dir))
        print(f' {dep_key} -> {src_pkg_relpath}')
        deps[dep_key] = item(value('{ path = "' + src_pkg_relpath + '", develop = true }'))
        return True
    return False


def get_freshest_pkg_path(dir_path: str, pkg_name_beginning: str) -> str:
    most_recent_file = None
    most_recent_time = 0
    for entry in os.scandir(dir_path):
        if match_package(pkg_name_beginning, entry.name):
            # get the modification time of the file
            mod_time = entry.stat().st_mtime_ns
            if mod_time > most_recent_time:
                # update the most recent file and its modification time
                most_recent_file = entry.path
                most_recent_time = mod_time
    return most_recent_file


def match_package(pkg_name_beginning: str, pkg_name: str) -> bool:
    if pkg_name_beginning in [pkg_name.removesuffix(".tar.gz"), pkg_name.removesuffix(".whl")]:
        return True

    regex: str = "^" + pkg_name_beginning + r"-\d+\.\d+\S*\.(?:tar\.gz|whl)"
    return re.match(regex, pkg_name)


def parse_commandline_args() -> Namespace:
    parser = ArgumentParser(
        description=textwrap.dedent(DESCRIPTION),
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('toml_path', help='path to the pyproject.toml to be modified')

    # Print help if no arguments provided.
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    return parser.parse_args()


def get_poetry_table(toml: TOMLDocument) -> items.Table:
    return toml['tool']['poetry']


def read_toml_file(filepath: str) -> TOMLDocument:
    exit_if_not_toml_file(filepath)
    toml = toml_file.TOMLFile(filepath).read()

    if 'tool' not in toml or 'poetry' not in toml['tool']:
        exit(f'NO Poetry in the toml file: {filepath}')

    return toml


def write_toml_file(output_path: str, toml: TOMLDocument):
    toml_file.TOMLFile(output_path).write(toml)
    print(f'Updated {output_path}')


def exit_if_not_toml_file(filepath: str):
    if not (path.isfile(filepath) and filepath.endswith('.toml')):
        exit(f'{filepath} is not a .toml file.')


if __name__ == '__main__':
    main()
