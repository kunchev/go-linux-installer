#! /usr/bin/env python3
"""Download and install Go on Linux, list all available versions on the
    Go website.

Attributes:
    chunk_size (int): Chunks size of the package, required for tqdm
    go_dl_base_url (str): Base Go download URL
    go_local (str): Local download folder on the filesystem
    go_url (str): URL with desired go package
"""

try:
    import argparse
    import requests
    import httplib2
    from tqdm import tqdm
    from bs4 import BeautifulSoup
    from bs4 import SoupStrainer
except ModuleNotFoundError as err:
    print('pip3 install -r requirements.txt')
    exit(err)


go_dl_base_url: str = 'https://golang.org/dl/'
go_url: str = 'https://golang.org/dl/go1.15.2.linux-amd64.tar.gz'
go_local: str = '/tmp/'
chunk_size: int = 1024


def get_go_versions(url):
    # TODO: call this function only when supplied argparse argument to
    #       list the available versions
    """Display all available Go packages for Linux

    Args:
        url (string): Base Go download URL

    Returns:
        go_linux_amd64_versions: All Go versions available on the site
        go_linux_amd64_links: All Go links available to download
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
    """Display all available Go download links with packages for Linux

    Args:
        url (string): Base Go download URL

    Returns:
        go_linux_amd64_links: All Go links to versions available
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
    """Call this function only when specific version is required

    Args:
        url (string): Base Go download URL
        version (int): Desired Go version in format x.yy.z

    Returns:
        go_linux_amd64_dl_link: Go link with desired version to be installed
    """
    go_linux_amd64_dl_link = []
    http = httplib2.Http()
    status, response = http.request(url)

    for link in BeautifulSoup(response, parse_only=SoupStrainer('a'),
                              features="html.parser"):
        if link.has_attr('href'):
            if 'linux-amd64' in link['href']:
                if version in link['href']:
                    # go_linux_amd64_dl_link.append(url + link[
                    # 'href'].lstrip('/dl/'))
                    go_linux_amd64_dl_link = url + link['href'].lstrip('/dl/')

    return go_linux_amd64_dl_link


def get_go(url, location):
    # TODO: this function downloads the currently defined package ver.
    # TODO: unzip the package and install the source code
    # TODO: create ~/go{src,pkg,bin} directories
    # TODO: to update ENV variables
    """Download and install desired Go package version for Linux

    Args:
        url (string): URL with desired go package
        location (string): Local download folder on the filesystem
    """
    r = requests.get(url, stream=True)
    total_size = int(r.headers['content-length'])
    filename = url.split('/')[-1]

    print(f'Downloading from {url}')
    with open(location + filename, 'wb') as f:
        for data in tqdm(iterable=r.iter_content(chunk_size=chunk_size),
                         total=total_size / chunk_size, unit='KB'):
            f.write(data)

    print(f'Download complete, file saved to {location + filename}')


def main():
    """Main function, entry point of program.
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
                        action='store', dest="action", default="listgoversions",
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
        go_versions = get_go_versions(go_dl_base_url)
        print(f'Available Go versions for Linux:\n{go_versions}')
        exit(0)

    # List all available Go download links on the Go website
    if args.action == 'listgolinks':
        go_links = get_go_links(go_dl_base_url)
        print(f'Available Go download links for Linux:\n{go_links}')
        exit(0)

    # Download and install the desired Go version
    if args.action == 'installgo':
        if args.version is not None:
            desired_version = args.version
            download_url = get_go_link(go_dl_base_url, desired_version)
        else:
            print('Please provide Go version as a value: 1.15.2')
            exit(1)
        print(
            f'You selected Go version {desired_version}, it will be '
            f'downloaded from {download_url}')
        get_go(download_url, go_local)


if __name__ == '__main__':
    main()