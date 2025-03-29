import os, requests, json, argparse

silent=False

def log(str):
  if(not silent):
    print(str)

class CloudflareDDNS:
  def __init__(self):
    secrets = self.get_secrets()

    self.api_key = secrets['api-key']
    self.zone_id = secrets['zone-id']
    self.records = secrets['records']

    self.headers = {
      'Authorization' : f'Bearer {self.api_key}',
      'Content-Type' : 'application/json'
    }

  def get_secrets(self):
    path=os.path.dirname(os.path.abspath(__file__)) 

    with open(f'{path}/secrets.json') as f:
      d=f.read()

    return json.loads(d)

  def get_current_ip(self):
    log('checking public ip...')
    ip=requests.get('https://api.ipify.org').text
    log(f'public ip: {ip}')
    return ip

  def api_get_call(self, endpoint):
    return requests.get(endpoint, headers=self.headers).text

  def api_put_call(self, endpoint, data):
    return requests.put(endpoint, headers=self.headers, data=data).text

  def build_record_data(self, domain):
    return {
      'type' : 'A',
      'name' : domain,
      'content' : self.ip,
      'proxied' : 'true'
    }

  def get_dns_records(self):
    return self.api_get_call(f'https://api.cloudflare.com/client/v4/zones/{self.zone_id}/dns_records/')

  def get_stored_ip(self, record_id):
    result = self.api_get_call(f'https://api.cloudflare.com/client/v4/zones/{self.zone_id}/dns_records/{record_id}')
    return json.loads(result)['result']['content']

  def update_stored_ip(self, record_id, name):
    data = self.build_record_data(name)
    self.api_put_call(f'https://api.cloudflare.com/client/v4/zones/{self.zone_id}/dns_records/{record_id}', data)
  
  def run_ddns(self):
    self.ip = self.get_current_ip()
    for record in self.records:
      log(f'checking stored ip for record {record['name']}...')
      stored_ip = self.get_stored_ip(record['id'])
      log(f'stored ip for {record['name']}: {stored_ip}')
      if stored_ip != self.ip:
        log(f'{record['name']} stored ip does not matche current public ip')
        log(f'updating stored ip for {record['name']}')
        self.update_stored_ip(record['id'], record['name'])
      else:
        log(f'{record['name']} stored ip matches current public ip')

parser = argparse.ArgumentParser(description="A dynamic-dns client for using the Cloudflare API")
parser.add_argument('-r', '--records', action='store_true', help='fetch the current dns records information')
parser.add_argument('-s', '--silent', action='store_true', help='enable silent run')
args = parser.parse_args()

cddns = CloudflareDDNS()

if(args.records):
  print(cddns.get_dns_records())
else:
  cddns.run_ddns()