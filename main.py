#!/ /usr/bin/python3

import json
import os
import sys
import zipfile
import urllib.request

import requests

MASA_BASE_URL = 'https://masa.dy.fi/tmp/minecraft/mods/client_mods/?mcver={mc_ver}&mod={mc_mod}'
MMC_JSON = 'mmc-pack.json'
MODS = ['litematica', 'itemscroller', 'malilib', 'minihud', 'tweakeroo']
MODS_FOLDER = '.minecraft/mods'

DUM_MASA_NAMING_MAP = {
    '20w10a': '1.16-snapshot-20w10a',
    '20w46a': '1.17-snapshot-20w46a',
    '20w48a': '1.17-snapshot-20w48a'
}


def main(action, data, extra_args):
    _zipfile = None
    if action == 'multimc':  # download to multimc instance
        mc_dir = data
        download_target = os.path.join(mc_dir, MODS_FOLDER)
        with open(os.path.join(mc_dir, MMC_JSON)) as f:
            mmc_json = json.load(f)

        minecraft_version = {c.get('cachedName'): c for c in mmc_json.get('components')}.get('Minecraft').get('version')
        minecraft_version = DUM_MASA_NAMING_MAP.get(minecraft_version, minecraft_version)

    elif action == 'modpackage':  # download to a folder or zipfile
        minecraft_version = DUM_MASA_NAMING_MAP.get(data, data)
        download_target = f'mods-{minecraft_version}'
        if '-a' in extra_args:  # make a zipfile of mods
            download_target = f'{download_target}.zip'
            if os.path.exists(download_target):
                if os.path.isfile(download_target):
                    print(f'fuck off, file exists: {download_target}')
                return
            else:
                _zipfile = zipfile.ZipFile(download_target, 'w')
        else:  # dump mods in a directory
            if not os.path.isdir(download_target):
                os.mkdir(download_target)

    else:
        print('fuck off, read the code you moron')
        return

    for mod in MODS:
        masa_mod_for_version = urllib.request.urlopen(MASA_BASE_URL.format(mc_ver=minecraft_version, mc_mod=mod))
        for l in masa_mod_for_version.readlines():
            line = l.decode()
            if 'Download</a>' in line:
                mod_link = line.strip().split('href="')[1].split('">Download')[0]
                if _zipfile is not None:
                    print(f'writing {mod_link} as {mod}.jar in the archive: {download_target}.zip')
                    _zipfile.writestr(f'{mod}.jar', urllib.request.urlopen(mod_link).read())
                    break
                else:
                    jar_name = os.path.join(download_target, f'{mod}.jar')
                    if os.path.isfile(jar_name) and not '-f' in extra_args:
                        print(f'skipping {mod} as its already there, run with \'-f\' if you really want it.')
                        break
                    else:
                        with open(jar_name, 'wb') as new_jar:
                            new_jar.write(urllib.request.urlopen(mod_link).read())
                            print(f'Downloaded {mod}')
                        break


def get_all_versions():
    page = requests.get(MASA_BASE_URL.split('?')[0])
    start = False
    for line in page.content.decode().splitlines():
        if 'Interesting' in line:
            start = True
        elif start:
            if 'snapshot' in line:
                print(line)
                continue
            if '<option' in line:
                yield line.split('>')[1].split('<')[0]


INDEX_LOCATION='index.html'

if __name__ == '__main__':
    if sys.argv[1] == 'generate-all-archives':
        for version in get_all_versions():
            print(version)
            continue
            main('modpackage', version, ['-a'])
            with open(INDEX_LOCATION, 'r') as download_page:
                current_page_data = download_page.read()
                if f'>{version}.zip<' in current_page_data:
                    continue

            with open(INDEX_LOCATION, 'w+') as download_page:
                download_page.write(f'{current_page_data}<a href=mods-{version}.zip>{version}.zip</a>\n')
        sys.exit()

    try:
        act, data = sys.argv[1], sys.argv[2]
    except IndexError:
        print('READ THE CODE')
        sys.exit(1)
    extra_args = sys.argv[3:]
    print(extra_args)
    main(act, data, extra_args)
