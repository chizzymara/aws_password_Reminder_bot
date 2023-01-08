import json
import datetime
import logging
import boto3
import csv
import logging
import time
import os
import requests
from functions.template import blocks

iam = boto3.client('iam')

logging.getLogger(__name__).setLevel(logging.INFO)
log = logging.getLogger(__name__)

SIGNIN_URL = os.environ['Signin_URL']
SLACK_TOKEN = os.environ['oauth']
AWS_ACCOUNT_ALIAS = os.environ['account_alias']

IMAGE_NORMAL = "https://media0.giphy.com/media/m7eBTQ5fVAdbiag2W7/giphy.gif?cid=ecf05e47j3zuptnupnlj6a1kys9e2uwqqn2qskm4hwnez384&rid=giphy.gif"
IMAGE_URGENT = "https://media.giphy.com/media/26n6xBpxNXExDfuKc/giphy-downsized.gif"
IMAGE_CRITICAL = "https://media.giphy.com/media/YiJJOWlaCmNmUIlMBI/giphy-downsized.gif"

BLOCKS = blocks


class ExceptionGenerateReport(Exception):
    pass


class ExceptionGetReport(Exception):
    pass


class ExceptionFormatReport(Exception):
    pass


class ExceptionGetNextPasswordRotation(Exception):
    pass


class ExceptionMatchUserToSlack(Exception):
    pass


class ExceptionSendSlackMessage(Exception):
    pass


class ExceptionPrepareMessage(Exception):
    pass


def lambda_handler(event, context):
    report = generate_report()
    for attempt in range(10):
        try:
            decoded_content = get_report(report)
        except ExceptionGetReport:
            time.sleep(1)
            continue
        else:
            break
    content_dict = format_report(decoded_content)
    metadata = get_next_password_rotation(content_dict)
    users_dictionary = match_user_to_slack(metadata)
    response = send_slack_message(users_dictionary)
    return {
        'status': str(response)
    }


def generate_report():
    try:
        report = iam.generate_credential_report()
        return report
    except Exception as exc:
        logging.exception(exc)
        raise ExceptionGenerateReport from exc


def get_report(report):
    try:
        content = iam.get_credential_report()
        # convert from bytes to string
        decoded_content = content["Content"].decode("utf-8")
        return decoded_content
    except Exception as exc:
        logging.exception(exc)
        raise ExceptionGetReport from exc


def format_report(decoded_content):
    try:
        content_lines = decoded_content.split("\n")

        # Initiate the reader, convert that to a list and turn that into a dict
        content_reader = csv.DictReader(content_lines, delimiter=",")
        content_dict = dict(enumerate(list(content_reader)))
        return content_dict
    except Exception as exc:
        logging.exception(exc)
        raise ExceptionFormatReport from exc


def get_next_password_rotation(content_dict):
    try:
        expiry_dict = {"users": []}
        today = datetime.datetime.now().date()
        for user in content_dict:
            if content_dict[user]['password_enabled'] == 'true':
                user_name=content_dict[user]['user']
                next_rotation=content_dict[user]['password_next_rotation']
                next_rotation_date = datetime.datetime.strptime(next_rotation.split('T')[0], '%Y-%m-%d').date()
                diff = (next_rotation_date - today).days
                small_dict = {
                    "user":{
                        "username": user_name,
                        "expires_in": diff,
                    }
                }
                expiry_dict["users"].append(small_dict)
        return expiry_dict
    except Exception as exc:
        logging.exception(exc)
        raise ExceptionGetNextPasswordRotation from exc


def match_user_to_slack(metadata):
    try:

        users_dictionary=metadata
        for users in users_dictionary.values():
            for user in users:
                response = iam.list_user_tags(
                    UserName=user["user"]["username"]
                )
                for tags in response["Tags"]:
                    if tags['Key'] == 'user:slack_id':
                        slack_id = tags['Value']
                        user["user"]["user:slack_id"]=slack_id

        return users_dictionary
    except Exception as exc:
        logging.exception(exc)
        raise ExceptionMatchUserToSlack from exc


def prepare_message(first_name,days):
    try:

        message_body = BLOCKS
        text_normal = " *Hello* " + first_name.capitalize() + " *your* " + AWS_ACCOUNT_ALIAS + " AWS password expires in* " +  days + " *days* :exclamation: Please update your password as soon as possible."
        text_urgent = " *Hello* " + first_name.capitalize() + " *your* " + AWS_ACCOUNT_ALIAS + " AWS password expires in* " +  days + " *days* :exclamation: You need to update your password as soon as possible :alarm_clock: :alarm_clock: "
        text_critical = " *Hello* " + first_name.capitalize() + " *your* " + AWS_ACCOUNT_ALIAS + " AWS password expires in* " + days + " *days* :exclamation: \nThis is a final reminder to change your password :exclamation: \nYou will be locked out of your account and will need to contact your admin to reset you password after today :exclamation: :exclamation:"

        if int(days) in [14,7]:
            message_body[0]["image_url"]=IMAGE_NORMAL
            message_body[1]["text"]["text"]=text_normal
        elif int(days) in [3,2]:
            message_body[0]["image_url"]=IMAGE_URGENT
            message_body[1]["text"]["text"]=text_urgent
        elif int(days) == 1:
            message_body[0]["image_url"]=IMAGE_CRITICAL
            message_body[1]["text"]["text"]=text_critical
        return message_body
    except Exception as exc:
        logging.exception(exc)
        raise ExceptionPrepareMessage from exc


def send_slack_message(users_dictionary):
    try:

        for users in users_dictionary.values():
            for user in users:
                global response
                first_name = user["user"]["username"].split('.')[0]
                days = str(user["user"]["expires_in"])
                slack_id = user["user"]["user:slack_id"]
                header = ":pager: AWS PASSWORD REMINDER."
                log.info("User: "+str(user["user"]["username"])+", slack ID: "+str(slack_id)+", password expires in "+str(days)+" days")

                message=prepare_message(first_name,days)
                data = {'token': SLACK_TOKEN, 'channel': slack_id, 'as_user': True, 'text': header, 'blocks': json.dumps(message)}
                if int(days) in [14 , 7 , 3 , 2 , 1]:
                    #comment / uncomment this to send to actual slack users
                    response = requests.post(url='https://slack.com/api/chat.postMessage', data=data)
                    print("message has been sent to " + first_name + " with " + days+ " days left.")

    except Exception as exc:
        logging.exception(exc)
        raise ExceptionSendSlackMessage from exc
