import os
import requests
from cloudflare import Cloudflare

def get_google_addresses():
    """Henter alle IPv4- og IPv6-adresser, der bruges af Google."""
    r = requests.get("https://www.gstatic.com/ipranges/goog.json")
    r.raise_for_status()
    data = r.json()["prefixes"]
    ips = [entry["ipv4Prefix"] for entry in data if "ipv4Prefix" in entry]
    ips += [entry["ipv6Prefix"] for entry in data if "ipv6Prefix" in entry]
    return ips

def update_access_group():
    """Opdaterer Cloudflare Access Group med de hentede Google IP-adresser."""
    token = os.environ["CF_TOKEN"]
    account_id = os.environ["CF_ACCOUNT_ID"]
    group_id = os.environ["CF_ACCESSGROUP_ID"]

    ips = get_google_addresses()
    client = Cloudflare.from_token(token)

    data = {
        "include": [{"ip": {"ip": ip}} for ip in ips],
        "exclude": [],
        "require": []
    }

    client.zero_trust.access.groups.update(
        group_id=group_id,
        account_id=account_id,
        params=data
    )
    print("Access group updated successfully.")

if __name__ == "__main__":
    update_access_group()
