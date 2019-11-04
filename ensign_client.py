import requests
import json

jwt = 'TOKEN_GOES_HERE'

def get_headers(token):
    return {
        "Authorization": "Bearer " + token
    }


def update_flag(environment, app, namespace, name, percentage):
    headers = get_headers(jwt)
    data = {
        "selector": "channels:stable",
        "value": {
            "percentOf": {
                "clients": percentage
            }
        },
        "created_by": "The Knob"
    }

    res = requests.put(
        "https://api.unbounce.com/ensign/"+environment+"/flags/"+app+"/"+namespace+"/"+name, json=data, headers=headers)

    return res.json()


def get_percentage(environment, app, namespace, name):
    headers = get_headers(jwt)

    res = requests.get(
        "https://api.unbounce.com/ensign/"+environment+"/flags/"+app+"/"+namespace+"/"+name+"?selector=channels:stable", headers=headers)

    val = res.json()['flag']['value']

    if isinstance(val, dict) and 'percentOf' in val and 'clients' in val['percentOf']:
        return val['percentOf']['clients']
    else:
        return 0


res = get_percentage('integration', 'ub-amp-ui', 'features', 'tabbedOverview')

print(res)
