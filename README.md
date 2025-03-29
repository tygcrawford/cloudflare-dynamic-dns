# Cloudflare DDNS

## Secrets File

Place a secrets.json file in the repository root directory with the following structure:

```json
{
  "api-key": "<cloudflare-api-key>",
  "zone-id": "<cloudflare-domain-zone-id>",
  "records": [
    {
      "name": "<record-1-name>",
      "id": "<record-1-id>"
    },
    {
      "name": "<record-2-name>",
      "id": "<record-2-id>"
    }
  ]
}
```
