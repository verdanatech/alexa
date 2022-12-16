import logging
import os
import boto3
from botocore.exceptions import ClientError
import requests
import time
import json
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model.services.directive import (
    SendDirectiveRequest, Header, SpeakDirective)
import time
import random

#CONSTANTES
ALEXA_TOKEN_KEY = "ALEXA_KEY"
VCONNECTOR_API_URL = "https://vconnector2.verdanadesk.com/api"



def create_presigned_url(object_name):
    """Generate a presigned URL to share an S3 object with a capped expiration of 60 seconds

    :param object_name: string
    :return: Presigned URL as string. If error, returns None.
    """
    s3_client = boto3.client('s3',
                             region_name=os.environ.get('S3_PERSISTENCE_REGION'),
                             config=boto3.session.Config(signature_version='s3v4',s3={'addressing_style': 'path'}))
    try:
        bucket_name = os.environ.get('S3_PERSISTENCE_BUCKET')
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=60*1)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response



def check_account_linking(handler_input):
    print("CHECK ACCOUNT_LINKING")
    access_token = handler_input.request_envelope.context.system.user.access_token
    #return (access_token == None)
    if (access_token == None):
        raise ValueError("account_linking")

def vconnector_post(api_endpoint, data, handler_input):
    url = '{api_url}{api_endpoint}'.format(api_url=VCONNECTOR_API_URL, api_endpoint=api_endpoint)
    access_token = handler_input.request_envelope.context.system.user.access_token
    device_id = handler_input.request_envelope.context.system.device.device_id
    email = handler_input.service_client_factory.get_ups_service().get_profile_email()
    
    data["email"] = email
    data["device_id"] = device_id

    headers = {
        'alexa-key': 'ALEXA_KEY',
        'account-jwt': access_token
    }
    
    try:
        r = requests.post(url, headers=headers, json=data)
        response = r.json()
        #response["status"]
        return response
    except Exception as e:
        print(e)
        return None

def vconnector_get(api_endpoint, data, handler_input):
    url = '{api_url}{api_endpoint}'.format(api_url=VCONNECTOR_API_URL, api_endpoint=api_endpoint)
    access_token = handler_input.request_envelope.context.system.user.access_token
    device_id = handler_input.request_envelope.context.system.device.device_id
    email = handler_input.service_client_factory.get_ups_service().get_profile_email()

    data["email"] = email
    data["device_id"] = device_id

    headers = {
        'alexa-key': 'ALEXA_KEY',
        'account-jwt': access_token
    }
    
    try:
        r = requests.get(url, headers=headers, json=data)
        response = r.json()
        #response["status"]
        return response
    except Exception as e:
        print(e)
        return None


def get_progressive_response(handler_input):
    # type: (HandlerInput) -> None
    request_id_holder = handler_input.request_envelope.request.request_id
    directive_header = Header(request_id=request_id_holder)
    speech = SpeakDirective(speech="Ok, um momentinho só!")
    directive_request = SendDirectiveRequest(
        header=directive_header, directive=speech)

    directive_service_client = handler_input.service_client_factory.get_directive_service()
    directive_service_client.enqueue(directive_request)
    return