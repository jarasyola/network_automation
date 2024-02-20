# The script checks if the domain is active and if is pointing to the actual server
import subprocess
import socket

def check_domain_info(domain, target_ip):
    try:
        # Run the whois command for the domain
        result = subprocess.run(['whois', domain], capture_output=True, text=True)

        # Check if the WHOIS response contains the domain name
        if domain.lower() not in result.stdout.lower():
            print(f"\n{domain} does not exist.")
            return False

        # Check if either A or MX record points to the target IP
        try:
            # Check if the A record points to the target IP
            a_record_ip = socket.gethostbyname(domain)

            # Check if the MX record points to the target IP
            mx_record_ip = socket.gethostbyname_ex(domain)[2][0]

            if a_record_ip == target_ip or mx_record_ip == target_ip:
                print(f"\n{domain} is active and pointing to server {target_ip}.")
            else:
                print(f"\n{domain} is active, but none of the DNS RECORDS IS POINTING TO THE SERVER {target_ip}.")

        except socket.gaierror as e:
            print(f"\nError resolving DNS for {domain}: {e}")
            print(f"\n{domain} is active, but THERE WAS AN ISSUE IN RESOLVING DNS RECORDS.")

        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

# Replace 'your_target_ip' with the IP address you want to check against
target_ip = 'X.X.X.X'

# Replace the string with your domains separated by spaces
domains_to_check_string = """
somedomain.co.tz
somedomain.com



"""

# Split the domains string into a list of domains
domains_to_check = domains_to_check_string.split()

# Iterate through each domain and check information
for domain in domains_to_check:
    check_domain_info(domain, target_ip)
