#! /usr/bin/env python3
"""Download and install Go on Linux, list all available versions on the
    Go website.

Attributes:
    chunk_size (int): Chunks size of the package, required for tqdm
    go_dl_base_url (str): Base Go download URL
    go_local (str): Local download folder on the filesystem
    go_url (str): URL with desired go package
"""

# work in progress...

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


# TODO: change the names of the variables with more proper ones
go_dl_base_url: str = 'https://golang.org/dl/'
go_url: str = 'https://golang.org/dl/go1.15.2.linux-amd64.tar.gz'
go_local: str = '/tmp/'
chunk_size: int = 1024


# TODO: implement argparser to get the current available Go versions
# TODO: pass the results from the argparser desired version argument
#       to the installation function


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
    # TODO: call this function only when specific version is required,
    #       return result with link corresponding the package version
    #       selected from the get_go_versions function
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


def get_go(url, location):
    # TODO: this function downloads the currently defined package ver.
    # TODO: to unzip the package and install the source code
    # TODO: to create ~/go{src,pkg,bin} directories
    # TODO: to update ENV variables
    # TODO: download and install desired version - get results from the
    #       other two functions get_go_links, get_go_versions and
    #       combine via argparser, print selected version in the print
    #       statement below
    """Download Go package for Linux (go1.15.2.linux-amd64)

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
    parser = argparse.ArgumentParser(description='List available Go packages '
                                                 'for Linux on the official '
                                                 'Go website. Install the '
                                                 'selected package version '
                                                 'from the list.')

    args = parser.parse_args()
    go_versions = get_go_versions(go_dl_base_url)
    go_links = get_go_links(go_dl_base_url)

    # TODO: pretty print the list items, embed in argparser
    print(f'Available Go versions for Linux:\n{go_versions}')
    print(f'Available Go download links for Linux:\n{go_links}')

    # Download Go version 15.2.linux-amd64
    get_go(go_url, go_local)


if __name__ == '__main__':
    main()
