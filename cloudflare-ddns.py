import os, requests, json, argparse

class CloudflareDDNS:
  def __init__(self):
    secrets = self.get_secrets()

    self.api_key = secrets['api-key']
    self.zone_id = secrets['zone-id']
    self.records = secrets['records']

    self.ip = self.get_current_ip()
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
    return requests.get("https://ifcfg.me").text

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
    for record in self.records:
      stored_ip = self.get_stored_ip(record['id'])
      if stored_ip != self.ip:
        self.update_stored_ip(record['id'], record['name'])

parser = argparse.ArgumentParser(description="A dynamic-dns client for using the Cloudflare API")
parser.add_argument('-r', '--records', action='store_true', help='fetch the current dns records information')
args = parser.parse_args()

cddns = CloudflareDDNS()

if(args.records):
  print(cddns.get_dns_records())
else:
  cddns.run_ddns()