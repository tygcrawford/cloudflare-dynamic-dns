#!/bin/bash

# get env vars and params
source $(dirname "$0")/.env

# get current public ip
echo "checking public ip..."
public_ip=$(curl -s ifcfg.me)

# function to update DNS record to current public ip
function update_record() {
  echo "updating dns record..."
  curl --silent --request PUT \
    --url "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records/${RECORD_ID}" \
    --header "Authorization: Bearer ${DDNS_API_TOKEN}" \
    --header "Content-Type: application/json" \
    --data '{"type":"A","name":"rollforrizz","content":"'${public_ip}'","proxied":true}'
}

# get the ip currently stored in the record
echo "retreiving stored ip..."
stored_ip=$(curl --silent --request GET \
  --url "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/dns_records/${RECORD_ID}" \
  --header "Authorization: Bearer ${DDNS_API_TOKEN}" \
  --header "Content-Type: application/json")
stored_ip=$(echo $stored_ip | jq ".result.content" | tr -d '"')

# if the currently stored ip doesn't match the public ip then update the record

if [ "${stored_ip}" != "${public_ip}" ]; then
  echo "record does not match current ip."
  update_record
else
  echo "record matches current ip."
fi
echo "done."
