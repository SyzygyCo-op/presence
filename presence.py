import requests
import sys
import datetime

DIRECTORY = os.path.dirname(os.path.realpath(__file__)) + '/'
sys.path.append(DIRECTORY)

from UnifiAPI.UnifiAPI import UnifiAPI
import secrets

PREV_FILE = DIRECTORY + 'prev.txt'
EXCLUDE_FILE = DIRECTORY + 'exclude.txt'
excludelist = []

def getClients():
    u = UnifiAPI(username=secrets.UNIFI_USER, password=secrets.UNIFI_PASS)
    return u.list_clients()['data']

def filter(device):
    if device['mac'] in excludelist:
        return False

    last_seen = datetime.datetime.fromtimestamp(device['last_seen'])
    if datetime.datetime.now() - last_seen > datetime.timedelta(minutes=1):
        return False

    if 'hostname' in device:
        host = device['hostname']
    else:
        host = device['oui']

    hostlower = host.lower()
    if 'android' in hostlower:
        return True
    if 'iphone' in hostlower:
        return True
    if 'galaxy' in hostlower:
        return True
    if 'LG' in host or 'Lg' in host:
        return True
    if 'Motorola' in host:
        return True
    if 'huawei' in hostlower:
        return True
    if 'xpeira' in hostlower:
        return True
    if 'blackberry' in hostlower:
        return True
    if 'Windows-Phone' in host:
        return True

    if 'Macbook' in host:
        return False

    return False

def sendToSlack(number):
    webhook_url = secrets.SLACK_PRESENCE_HOOK
    slack_data = {'text': '~' + str(number) + ' people present'}
    requests.post(webhook_url, json=slack_data)

if __name__ == '__main__':
    prev = 0
    try:
        with open(PREV_FILE) as f:
            prev = int(f.readline())
    except FileNotFoundError:
        pass

    try:
        with open(EXCLUDE_FILE) as f:
            for line in f:
                excludelist.append(line.strip())
    except FileNotFoundError:
        pass

    d = getClients()
    filtered = [x for x in d if filter(x)]
    num = len(filtered)
    print(num)

    for x in filtered:
        last_seen = datetime.datetime.now() - datetime.datetime.fromtimestamp(x['last_seen'])
        if 'hostname' in x: print(x['hostname'] + ': ' + str(last_seen))
        else: print(x['oui'] + ': ' + str(last_seen))

    if num != prev:
        with open(PREV_FILE) as f:
            f.write(str(num))
        sendToSlack(num)
        print('Slack message sent')
