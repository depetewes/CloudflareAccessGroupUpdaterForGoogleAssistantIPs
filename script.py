import cloudflare
import requests

def get_google_addresses():
    r = requests.get("https://www.gstatic.com/ipranges/goog.json")
    r.raise_for_status()
    ips = [ entry['ipv4Prefix'] for entry in r.json()['prefixes'] if 'ipv4Prefix' in entry ]
    ips += [ entry['ipv6Prefix'] for entry in r.json()['prefixes'] if 'ipv6Prefix' in entry ]
    return ips

def update_access_group(token, account_id, group_id, ips):
    cf = cloudflare.Cloudflare(token=token)  # Korrekt brug af CloudFlare SDK
    
    data = {
        "include": [ {"ip": {"ip": ip}} for ip in ips ],
        "exclude": [],
        "require": []
    }
    cf.accounts.access.groups.put(account_id, group_id, data=data)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="CloudFlare Google Assistant Access Group updater")
    parser.add_argument("--account", required=True, help="CF account ID")
    parser.add_argument("--token", required=True, help="CF API key")
    parser.add_argument("--group", required=True, help="ID of CF Access group that needs to be updated")
    args = parser.parse_args()

    ips = get_google_addresses()
    update_access_group(args.token, args.account, args.group, ips)
