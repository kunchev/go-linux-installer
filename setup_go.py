#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Download and install Go on Linux, list all available versions on the
Go website, select version to install and pass it as an argument.

- Go is an open source programming language:
https://golang.org/doc/copyright.html

- Linux is a family of open-source Unix-like operating systems based on
the Linux kernel:
https://www.kernel.org/category/about.html

- Python is an interpreted, high-level, dynamically typed,
garbage-collected and general-purpose programming language:
https://en.wikipedia.org/wiki/Python_Software_Foundation_License
https://docs.python.org/3/license.html


Attributes:
    chunk_size (int): Chunks size of the package, required for tqdm
    go_dl_base_url (str): Base Go download URL
    go_local (str): Local download folder on the filesystem
    go_home (str): /home/user/go (home go folder for projects)
    go_folders (tuple): /home/user/go/('src', 'pkg', 'bin')
    go_install_home (str): '/usr/local' (go installation folder)
"""

# TODO: Implement a separate function for the argparse with return
# TODO: Implement color print based on message type - green for ok,
#  red for error messages and blue for informational messages

# TODO: Validate format of the input parameter for the Go version - must
#  follow x.y, x.yy, x.y.z or x.yy.z pattern, where x y and z are digits
#  0 to 9

# TODO: Add argparse argument '--action checkgo' to check whether go is
#  already installed and if so - print the currently installed version

__author__ = 'Petyo Kunchev'
__version__ = '1.0.11'
__maintainer__ = 'Petyo Kunchev'
__status__ = 'Development'
__license__ = 'MIT'

import os
import time
import subprocess
from os import environ
from pathlib import Path
from typing import List, Any
from functools import partial

try:
    import argparse
    import requests
    import httplib2
    from tqdm import tqdm
    from bs4 import BeautifulSoup
    from bs4 import SoupStrainer
except ModuleNotFoundError as err:
    exit(f'Error: {err}, run \'pip3 install -r requirements.txt\'')


go_dl_base_url: str = 'https://golang.org/dl/'
go_local: str = '/tmp/'
chunk_size: int = 1024
go_home: str = str(Path.home()) + '/go/'
go_folders: tuple = ('src', 'pkg', 'bin')
go_install_home: str = '/usr/local'
current_shell: str = environ['SHELL']


def check_exists_dl_folder(folderpath):
    """
    Check if the local download folder exists.

    Args:
        folderpath (string): Path to the download folder
    """
    if not os.path.exists(folderpath):
        print(f'The desired download folder {folderpath} does not exist')
        exit(1)


def get_go_versions(url):
    """
    Display all available Go packages for Linux.

    Args:
        url (string): Base Go download URL

    Returns:
        go_linux_amd64_versions: All Go versions available on the site
    """
    go_linux_amd64_versions = []
    http = httplib2.Http()
    status, response = http.request(url)

    assert isinstance(response, object)
    for link in BeautifulSoup(response, parse_only=SoupStrainer('a'),
                              features="html.parser"):
        if link.has_attr('href'):
            if 'linux-amd64' in link['href']:
                go_linux_amd64_versions.append(link['href'].lstrip(
                    '/dl/go').rstrip('.linux-amd64.tar.gz'))

    return go_linux_amd64_versions


def get_go_links(url):
    """
    Display all available Go download links with packages for Linux
    on the Go website.

    Args:
        url (string): Base Go download URL

    Returns:
        go_linux_amd64_links: All Go links available to download
    """
    go_linux_amd64_links = []
    http = httplib2.Http()
    status, response = http.request(url)

    for link in BeautifulSoup(response, parse_only=SoupStrainer('a'),
                              features="html.parser"):
        if link.has_attr('href'):
            if 'linux-amd64' in link['href']:
                go_linux_amd64_links.append(url + link['href'].lstrip('/dl/'))

    return go_linux_amd64_links


def get_go_link(url, version):
    """
    Call this function only when specific version is required.

    Args:
        url (string): Base Go download URL
        version (int): Desired Go version in formats x.y, x.y.z, x.yy.z

    Returns:
        go_linux_amd64_dl_link: Go link with desired version selected
    """
    go_linux_amd64_dl_link: List[Any] = []
    http = httplib2.Http()
    status, response = http.request(url)

    for link in BeautifulSoup(response, parse_only=SoupStrainer('a'),
                              features="html.parser"):
        if link.has_attr('href'):
            if 'linux-amd64' in link['href'] and version in link['href']:
                go_linux_amd64_dl_link = url + link['href'].lstrip('/dl/')

    return go_linux_amd64_dl_link


def get_go(url, location):
    """
    Download and install desired Go package version for Linux, untar
    the downloaded package and place the contents in /usr/local/go.

    Args:
        url (string): URL with desired go package
        location (string): Local download folder on the filesystem
    """
    r = requests.get(url, stream=True)
    total_size = int(r.headers['content-length'])
    filename = url.split('/')[-1]
    tar_path = location + filename

    # 1. Download the desired Go archive
    with open(location + filename, 'wb') as f:
        for data in tqdm(iterable=r.iter_content(chunk_size=chunk_size),
                         total=total_size / chunk_size, unit='KB'):
            f.write(data)
    print(f'Download complete, archive saved to {tar_path}')

    # 2. Extract the downloaded archive,
    # check if Go is installed - exit if /usr/local/go is present
    if os.path.exists('/usr/local/go'):
        exit('go is installed')
    print(f'Extracting the archive contents from {tar_path} and '
          f'installing Go in /usr/local/go/, make sure that your user is in '
          f'the sudoers list')
    try:
        os.system(f'sudo tar -C {go_install_home} -xzf {tar_path}')
    except IOError as e:
        print(f'Error {e}, could not open {tar_path}')
        exit(1)


def ensure_go_home(root_dir, subfolders):
    """
    Create go folders /home/<user>/go/{src,pkg,bin}.

    Args:
        root_dir: /home/<user>/go/
        subfolders: src, pkg, bin (provided in set)
    """
    concat_path = partial(os.path.join, root_dir)
    mkdirs = partial(os.makedirs, exist_ok=True)
    for path in map(concat_path, subfolders):
        mkdirs(path)


def append_gopath_to_env(envfile: str):
    """
    Append the go path to the user's shell profile.

    Args:
        envfile (str): path to the env file, auto generated
    """
    # open the current active shell source file and append the go path
    print('Appending go path to $PATH')
    with open(envfile, 'a') as f:
        f.write('\n' + 'export PATH=$PATH:/usr/local/go/bin' + '\n')
        f.close()

    # source the updated envfile
    subprocess.call(['.', envfile], shell=True)


def handle_os_environment():
    """
    Update ENV .bashrc or .zshrc, '/etc/profile'.
    """
    glob_profile_config: str = '/etc/profile'
    user_home: str = str(Path.home()) + '/'

    if 'zsh' in current_shell:
        shell_rc: str = user_home + '.zshrc'
        print(f'Current shell config: {shell_rc}')
        append_gopath_to_env(shell_rc)
    elif 'bash' in current_shell:
        shell_rc: str = user_home + '.bashrc'
        print(f'Current shell config: {shell_rc}')
        append_gopath_to_env(shell_rc)
    else:
        print('Shell config file is unknown')

    print(f'Global shell config: {glob_profile_config}')
    print('Verify installation by running: \'go version\' from your terminal')


def main():
    """
    Main function, entry point of program, argparser is used here in
    combination with the functions defined in this module.
    """
    download_url = None
    desired_version = None
    parser = argparse.ArgumentParser(description='List available Go packages '
                                                 'for Linux on the official '
                                                 'Go website. Install the '
                                                 'selected package version '
                                                 'from the list.')
    parser.add_argument('--action', '-a', metavar='<action>',
                        choices=['listgoversions', 'listgolinks', 'installgo'],
                        action='store', dest="action",
                        default="listgoversions",
                        help='[listgoversions, listgolinks, installgo] - the '
                             'action that will be taken. "listgoversions" '
                             'will list all available Go versions for Linux '
                             'on the Go website. "listgolinks" will list all '
                             'available Go download links on the Go website. '
                             '"installgo" will install the selected Go '
                             'version passed as a parameter value. Default: '
                             'listgoversions')
    parser.add_argument('--version', '-v', metavar='<version>', action='store',
                        dest="version",
                        help='Specifies the version of Go to be installed, '
                             'for example: 1.15.2')
    args = parser.parse_args()

    # List all available Go versions on the Go website
    if args.action == 'listgoversions':
        go_versions: list = get_go_versions(go_dl_base_url)
        print('Available Go versions for Linux:')
        # start from the second (1), not first (0) element, because the
        # value of the first (0) can have duplicates - 1.15 1.15 gets
        # parsed twice
        for version in range(1, len(go_versions)):
            print('Go ver:', go_versions[version])
        exit(0)

    # List all available Go download links on the Go website
    if args.action == 'listgolinks':
        go_links: list = get_go_links(go_dl_base_url)
        print('Available Go download links for Linux:')
        # start from the second (1), not first (0) element, because the
        # value value of the first (0) can have duplicates with the
        # second (1) element
        for link in range(1, len(go_links)):
            print('Download link for Go ver:', go_links[link])
        exit(0)

    # Download and install the desired Go version from the Go website
    if args.action == 'installgo':
        # First check if the download folder is present - 'go_local'
        check_exists_dl_folder(go_local)
        if args.version is not None:
            desired_version = args.version
            download_url = get_go_link(go_dl_base_url, desired_version)
        else:
            print('Please provide Go version as a value: 1.15.2')
            exit(1)
        print(
            f'Selected Go version: {desired_version}, downloading Go '
            f'package from: {download_url}')
        setup_start = time.perf_counter()
        get_go(download_url, go_local)
        ensure_go_home(go_home, go_folders)
        handle_os_environment()
        setup_end = time.perf_counter()
        print(f'Completed in {round(setup_end - setup_start, 2)} second(s)')


if __name__ == '__main__':
    main()
