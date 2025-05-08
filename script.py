from cloudflare import Cloudflare
import requests
import os

def get_google_addresses():
    r = requests.get("https://www.gstatic.com/ipranges/goog.json")
    r.raise_for_status()
    ips = [entry['ipv4Prefix'] for entry in r.json()['prefixes'] if 'ipv4Prefix' in entry]
    ips += [entry['ipv6Prefix'] for entry in r.json()['prefixes'] if 'ipv6Prefix' in entry]
    return ips

def update_access_group():
    # Fetch token from environment variable
    token = os.getenv("CF_TOKEN")
    if not token:
        raise ValueError("CF_TOKEN environment variable not set.")
    
    # Initialize Cloudflare client using 'from_token'
    cf = Cloudflare.from_token(token)  # SDK v4.1.0: use from_token instead of passing token directly

    # Retrieve environment variables for account and group ID
    account_id = os.getenv("CF_ACCOUNT_ID")
    group_id = os.getenv("CF_ACCESSGROUP_ID")

    if not account_id or not group_id:
        raise ValueError("CF_ACCOUNT_ID or CF_ACCESSGROUP_ID environment variables not set.")
    
    ips = get_google_addresses()

    # Prepare data to update
    data = {
        "include": [{"ip": {"ip": ip}} for ip in ips],
        "exclude": [],
        "require": []
    }

    # Update the access group with new IPs
    cf.zero_trust.access.groups.update(group_id, account_id=account_id, **data)

if __name__ == "__main__":
    update_access_group()
