import argparse, datetime, random, time, sys

import requests, simplejson


# setup argparse so the user can change parameters from the command line
parser = argparse.ArgumentParser(description='Generates and submits sensor readings to Senslify.')
parser.add_argument('--min_val', dest='min_val', default=0, help='The minimum value to sample (default: 0).')
parser.add_argument('--max_val', dest='max_val', default=100, help='The maximum value to sample (default: 100).')
parser.add_argument('--interval', dest='interval', default=1, help='The number of seconds between samples (default: 1).')
parser.add_argument('--groupid', dest='groupid', default=0, help='The group identifier the sensor should be provisioned with (default: 0).')
parser.add_argument('--rtypeid', dest='rtypeid', default=0, help='The reading type identifier that the generated sensor readings belong to (default: 0).')
parser.add_argument('ip_addr', help='The IP address of the web server.')
args = parser.parse_args()

# grab the parsed parameters
min_val = float(args.min_val)
max_val = float(args.max_val)
interval = int(args.interval)
groupid = int(args.groupid)
rtypeid = int(args.rtypeid)
ip_addr = args.ip_addr

# send a provisioning request joining group 0
resp = requests.get(ip_addr + '/sensors/provision', params={'groupid': 0})
if resp.status_code == 403:
    print(resp.text)
    sys.exit(1)
json = resp.json()
sensorid = int(json['sensorid'])
sensor_alias = json['sensor_alias']
if 'group_alias' in json:
    group_alias = json['group_alias']

print(f'SensorID: {sensorid}')
print(f'Sensor Alias: {sensor_alias}')

# repeatedly generate and upload sensor data per the given interval
while True:
    data = random.uniform(min_val, max_val)
    json = simplejson.dumps({
        'sensorid': sensorid,
        'groupid': groupid,
        'rtypeid': rtypeid,
        'ts': int(datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp()),
        'val': data
    })
    requests.post(ip_addr + '/sensors/upload', data=json)
    time.sleep(interval)