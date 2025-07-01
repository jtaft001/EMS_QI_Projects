from scapy.all import ARP, Ether, srp
from mac_vendor_lookup import MacLookup
import socket

# Set your subnet here
TARGET_SUBNET = "10.0.0.0/24"  # Adjust to match your LAN

def scan_network(subnet):
    print(f"Scanning {subnet}...")
    arp = ARP(pdst=subnet)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    result = srp(packet, timeout=2, verbose=0)[0]

    devices = []
    for sent, received in result:
        ip = received.psrc
        mac = received.hwsrc
        try:
            vendor = MacLookup().lookup(mac)
        except Exception:
            vendor = "Unknown"
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except Exception:
            hostname = "N/A"
        devices.append({
            "IP": ip,
            "MAC": mac,
            "Vendor": vendor,
            "Hostname": hostname
        })
    return devices

def print_devices(devices):
    print(f"{'IP':<15}{'MAC':<18}{'Vendor':<30}{'Hostname'}")
    print("-" * 80)
    for d in devices:
        print(f"{d['IP']:<15}{d['MAC']:<18}{d['Vendor']:<30}{d['Hostname']}")

def suggest_ha_integrations(devices):
    suggestions = []
    keywords = {
        "esp": "ESPHome",
        "tuya": "Tuya",
        "philips": "Philips Hue",
        "google": "Google Cast",
        "roku": "Roku",
        "amazon": "Alexa",
        "sonos": "Sonos",
        "wyze": "Wyze",
        "leviton": "My Leviton",
        "netgear": "Netgear",
        "apple": "HomeKit",
        "shelly": "Shelly",
        "tplink": "TP-Link (Kasa/Deco)",
    }
    for d in devices:
        for keyword, integration in keywords.items():
            if keyword in d['Vendor'].lower() or keyword in d['Hostname'].lower():
                suggestions.append((d['IP'], integration))
    return suggestions

# Run the script
devices = scan_network(TARGET_SUBNET)
print_devices(devices)

ha_matches = suggest_ha_integrations(devices)
print("\n🔌 Suggested Home Assistant Integrations:")
for ip, integration in ha_matches:
    print(f" - {integration} device found at {ip}")