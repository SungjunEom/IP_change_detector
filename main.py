import base64
from email.message import EmailMessage

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from auth.auth import get_cred

import subprocess
import os


def check_ip():
  command = f"dig +short TXT o-o.myaddr.l.google.com @ns3.google.com"
  output = subprocess.check_output(command.split()).decode("utf-8")
  IP = str(output[1:-2])

  with open("./current_ip.txt","r") as f:
    before = f.read()
    if IP == before:
      return 0, IP
  
  with open("./current_ip.txt","w") as f:
    f.write(IP)
    return 1, IP


def gmail_send_message(IP):
  """Create and send an email message
  Print the returned  message id
  Returns: Message object, including message id

  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.
  """
  creds = get_cred()

  try:
    service = build("gmail", "v1", credentials=creds)
    message = EmailMessage()

    message.set_content(f"This is automated draft mail.\n\n IP has been changed to {IP}")

    message["To"] = "example@example.com"
    message["From"] = "example2@example.com"
    message["Subject"] = f"IP has been changed : {IP}"

    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {"raw": encoded_message}
    # pylint: disable=E1101
    send_message = (
        service.users()
        .messages()
        .send(userId="me", body=create_message)
        .execute()
    )
    print(f'Message Id: {send_message["id"]}')
  except HttpError as error:
    print(f"An error occurred: {error}")
    send_message = None
  return send_message


if __name__ == "__main__":
  flag, IP = check_ip()

  if flag == 0:
    exit()

  gmail_send_message(IP)