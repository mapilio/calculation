import urllib.request
import json
from typing import Dict, Any

from calculation.util import __name__ as name
from calculation.util import __major__ as major
from calculation.util import __minor__ as minor
from calculation.util import __patch__ as patch


def update_version(reqs: list, major: bool, minor: bool, patch:bool) -> str:
    version = {}
    version['major'] = reqs[0]
    version['minor'] = reqs[1]
    version['patch'] = reqs[2]
    print(f"Old Version = {version['major']}.{version['minor']}.{version['patch']}")
    if patch:
        version['patch'] += 1
    if minor:
        version['patch'] = 0
        version['minor'] += 1
    if major:
        version['patch'] = 0
        version['minor'] = 0
        version['major'] += 1
    new_version = str(version['major']) + "." + str(version['minor']) + "." + str(version['patch'])
    return new_version

def new_version(package: str, major: bool=False, minor:bool=False, patch:bool=True) -> str:
    req = urllib.request.Request(f'https://pypi.python.org/pypi/{package}/json')
    r = urllib.request.urlopen(req)
    if r.code == 200:
        t = json.loads(r.read())
        releases = t['info']['version']
        if releases:
            results = list(map(int, releases.split(".")))
            return update_version(results,major,minor,patch)


__version__ = new_version(name, major, minor, patch)
