import os
from cloudflare import Cloudflare
import requests

# Hent API-token, konto-ID og adgangsgruppe-ID fra miljøvariabler (som defineret i GitHub Actions secrets)
api_token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
group_id = os.environ.get("CLOUDFLARE_GROUP_ID", "")  # Den specifikke adgangsgruppe, du vil opdatere

# Hvis nogen af de nødvendige miljøvariabler mangler, stopper scriptet
if not api_token or not account_id or not group_id:
    print("API Token, Account ID, and Group ID are required as environment variables.")
    exit(1)

# Hent Google IP-adresser (Google Assistant IP ranges)
def get_google_addresses():
    r = requests.get("https://www.gstatic.com/ipranges/goog.json")
    r.raise_for_status()  # Hvis der er en fejl, stoppes scriptet
    ips = [entry['ipv4Prefix'] for entry in r.json()['prefixes'] if 'ipv4Prefix' in entry]
    ips += [entry['ipv6Prefix'] for entry in r.json()['prefixes'] if 'ipv6Prefix' in entry]
    return ips

# Opdater adgangsgruppen i Cloudflare
def update_access_group():
    # Initialiser Cloudflare-klienten med API-tokenet
    cf = Cloudflare.from_token(api_token)

    # Hent IP-adresserne fra Google Assistant
    ips = get_google_addresses()

    # Forbered dataen til opdateringen af adgangsgruppen
    data = {
        "include": [{"ip": {"ip": ip}} for ip in ips],  # Vi inkluderer IP-adresserne i gruppen
        "exclude": [],
        "require": []
    }

    # Opdater adgangsgruppen i Cloudflare
    cf.zero_trust.access.groups.update(group_id, account_id=account_id, **data)

if __name__ == "__main__":
    update_access_group()
