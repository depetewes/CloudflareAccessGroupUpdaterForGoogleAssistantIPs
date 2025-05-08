import os
import requests
from cloudflare import Cloudflare

def get_google_addresses():
    """Hent alle Google IPv4 og IPv6 ranges fra deres offentlige JSON."""
    r = requests.get("https://www.gstatic.com/ipranges/goog.json")
    r.raise_for_status()
    data = r.json()["prefixes"]
    ips = [entry["ipv4Prefix"] for entry in data if "ipv4Prefix" in entry]
    ips += [entry["ipv6Prefix"] for entry in data if "ipv6Prefix" in entry]
    return ips

def update_access_group():
    """Opdater en Cloudflare Access Group med IP-adresser fra Google."""
    token = os.environ.get("CF_API_TOKEN")
    account_id = os.environ.get("CF_ACCOUNT_ID")
    group_id = os.environ.get("CF_ACCESSGROUP_ID")

    if not all([token, account_id, group_id]):
        raise ValueError("CF_API_TOKEN, CF_ACCOUNT_ID og CF_ACCESSGROUP_ID skal være sat som miljøvariabler.")

    client = Cloudflare(token=token)
    ips = get_google_addresses()

    params = {
        "include": [{"ip": {"ip": ip}} for ip in ips],
        "exclude": [],
        "require": []
    }

    client.zero_trust.access.groups.update(
        group_id=group_id,
        account_id=account_id,
        params=params
    )

    print(f"Opdaterede Access Group {group_id} med {len(ips)} IP ranges.")

if __name__ == "__main__":
    update_access_group()
