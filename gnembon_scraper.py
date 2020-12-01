import requests
from github import Github

repos = {
    'carpet': 'gnembon/fabric-carpet',
    'extra': 'gnembon/carpet-extra',
    'autocrafting': 'gnembon/carpet-autoCraftingTable'
}

github = Github('bbd307e644cb53122a57d705b65876be92e93c74')


def main():
    ac_map = get_asset_map('autocrafting')
    extra_map = get_asset_map('extra')
    carpet_map = get_asset_map('carpet')
    common_versions = set(ac_map.keys()).intersection(extra_map.keys()).intersection(carpet_map.keys())
    print(ac_map['1.16.4'])
    print(extra_map['1.16.4'])
    print(carpet_map['1.16.4'])
    return
    for mc_version in common_versions:
        ac_c_map = ac_map[mc_version]
        extra_c_map = extra_map[mc_version]
        carpet_c_map = carpet_map[mc_version]
        common_carpet_versions = set(ac_c_map.keys()).intersection(extra_c_map.keys()).intersection(carpet_c_map.keys())
        if common_carpet_versions:
            carpet_version = max(common_carpet_versions)
            print(mc_version)
            print('ac', ac_map[mc_version][carpet_version])
            print('extra', extra_map[mc_version][carpet_version])
            print('carpet', carpet_map[mc_version][carpet_version])
            print()


def get_asset_map(repo):
    mc_carpet_map = {}
    for r in github.get_repo(repos[repo]).get_releases():
        for a in r.get_assets():
            try:
                mc_v, carpet_v = parse_asset_name(a.name)
                try:
                    mc_carpet_map[mc_v][carpet_v] = a.browser_download_url
                except KeyError:
                    mc_carpet_map[mc_v] = {carpet_v: a.browser_download_url}
            except NameError:
                pass
    return mc_carpet_map


def parse_asset_name(asset_name):
    _asset_prefix = ''
    _asset_suffix = ''
    if 'fabric-carpet-' in asset_name:
        _asset_prefix = 'fabric-carpet-'
        _asset_suffix = '+'
        if '+' not in asset_name:
            raise NameError
    elif 'carpet-extra-' in asset_name:
        if asset_name == 'carpet-extra-1.0.1.jar':
            raise NameError
        _asset_prefix = 'carpet-extra-'
        _asset_suffix = '.jar'
    elif 'carpet-autocrafting' in asset_name:
        if asset_name == 'carpet-autocraftingtable-1.16-20w13b-1.3.17.jar':
            return '20w13b', '1.3.17'

        _asset_prefix = 'carpet-autocraftingtable-'
        _asset_suffix = '.jar'

    for ignore in ('pre', 'infinite', 'rc1', '19w45ab'):
        if ignore in asset_name:
            raise NameError

    versions_only = asset_name.split(_asset_prefix)[1].split(_asset_suffix)[0]
    mc_version, carpet_version = versions_only.split('-')
    return mc_version, carpet_version


if __name__ == '__main__':
    main()