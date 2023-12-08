# This script is written to proactively send emails when clients signals are more than 
# the set threshold_signal 
# This works on Mikrotik radios/routers - tested on v6 and v7 ROS

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from librouteros import connect

def mikrotik_login(host, username, password):
    try:
        connection = connect(username=username, password=password, host=host)
        print(f"Connected to {host}")
        return connection
    except Exception as e:
        print(f"Failed to connect to {host}: {e}")
        return None

def get_users_with_bad_signal(connection, threshold_signal):
    try:
        users = connection(cmd='/interface/wireless/registration-table/print')
        bad_signal_users = [user for user in users if int(user.get('signal-strength')) < threshold_signal]
        return bad_signal_users
    except Exception as e:
        print(f"Error retrieving users: {e}")
        return []

def send_email(subject, body, to_emails, smtp_server, smtp_port, smtp_username, smtp_password):
    # Set up the MIME
    message = MIMEMultipart()
    message['From'] = smtp_username
    message['To'] = ', '.join(to_emails)
    message['Subject'] = subject

    # Attach the body of the email
    message.attach(MIMEText(body, 'plain'))

        # Append the email signatures
    signature = "\n\n-- Habari Node NOC Team --"
    message.attach(MIMEText(signature, 'plain'))

    # Connect to the SMTP server and send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_username, to_emails, message.as_string())
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    routers = [
        {"host": "router1_ip", "username": "username1", "password": "password1"},
        {"host": "router2_ip", "username": "username2", "password": "password2"},
        # Add more routers as needed
    ]

    threshold_signal = -75

    smtp_server = "your_smtp_server"
    smtp_port = 587
    smtp_username = "your_email@example.com"
    smtp_password = "your_email_password"
    to_emails = ["recipient1@example.com", "recipient2@example.com"]  # Add more email addresses as needed


    all_bad_signal_users = {}  # Accumulate bad signal users from all routers

    for router in routers:
        connection = mikrotik_login(router["host"], router["username"], router["password"])

        if connection:
            bad_signal_users = get_users_with_bad_signal(connection, threshold_signal)

            if bad_signal_users:
                all_bad_signal_users[router['host']] = bad_signal_users
                print(f"Users with bad signal on {router['host']} added to the list.")
            else:
                print(f"No users with bad signal on {router['host']}")
                continue  # Move to the next router

    if all_bad_signal_users:
        # Prepare and send a single email for all users with bad signals
        email_subject = "Clients with Bad Signal on Habari Network"
        email_body = "Dear Support,\n\nKindly find list of clients with bad signal across Habari Access Points and act proactively:\n"

        for router, users in all_bad_signal_users.items():
            email_body += f"\n Access Point IP: {router} :\n"
            for user in users:
                email_body += f"  Client: {user['radio-name']}, Signal Strength: {user['signal-strength']} dBm\n"

        send_email(email_subject, email_body, to_emails, smtp_server, smtp_port, smtp_username, smtp_password)
    else:
        print("No users with bad signal found on any access points.")

if __name__ == "__main__":
    main()
