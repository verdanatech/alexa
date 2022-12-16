# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder, CustomSkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.dispatch_components import AbstractRequestInterceptor
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model.services.directive import (
    SendDirectiveRequest, Header, SpeakDirective)
import time
from ask_sdk_core.api_client import DefaultApiClient

from ask_sdk_model import Response, IntentConfirmationStatus

from utils import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        check_account_linking(handler_input)
        
        ups_service = handler_input.service_client_factory.get_ups_service()
        email = ups_service.get_profile_email()
        
        speak_output = "Olá, eu sou a Vera, sua assistente da central de serviços GLPI . O que deseja fazer?"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class VerificarConexaoBaseIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (ask_utils.is_intent_name("VerificarConexaoBaseIntent")(handler_input))

    def handle(self, handler_input):
        check_account_linking(handler_input)
        
        speak_output = "Verificando conexão com a sua base!"
        
        retorno = vconnector_get("/alexa/dummy", {}, handler_input)
        print(retorno)
        if(retorno["status"] == "200"):
            try:
                speak_output = "Erro interno!"
                if(retorno["request"]["glpi"]):
                    speak_output = "Sua base está configurada e pronto para interagir comigo!"
            except:
                speak_output = "Não foi possível testar a conexão com sua base, por favor, verifique os dados de vínculo fornecidos!"
        else:
            speak_output = "Erro ao verificar conexão com sua base!"
        
        return (
            handler_input.response_builder
                .speak(speak_output).set_should_end_session(
            False)
                .response
        )


class VincularDispositivoIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (ask_utils.is_intent_name("VincularDispositivoIntent")(handler_input))

    def handle(self, handler_input):
        check_account_linking(handler_input)
        
        speak_output = "Vinculando este dispositivo na sua conta Verdana Desk!"
        
        retorno = vconnector_get("/alexa", {}, handler_input)
        
        if(retorno["status"] == "200"):
            if(retorno["auto_link"]):
                speak_output = "Parabéns! Seu dispositivo foi vinculado a sua conta!"
            else:
                speak_output = "Este dispositivo já possui um vínculo com sua conta!"
        else:
            speak_output = "Erro ao vincular seu dispositivo a sua conta!"
        
        return (
            handler_input.response_builder
                .speak(speak_output).set_should_end_session(
            False)
                .response
        )


class AberturaChamadoIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (ask_utils.is_intent_name("AberturaChamadoIntent")(handler_input))

    def handle(self, handler_input):
        check_account_linking(handler_input)
        
        confirmation = handler_input.request_envelope.request.intent.confirmation_status
        print(confirmation)
        if(confirmation == IntentConfirmationStatus.DENIED):
            speak_output = "Abertura de chamado cancelada!"
        else:
            speak_output = "Solicitando abertura de chamado em sua conta..."
            
            ticket_name = handler_input.request_envelope.request.intent.slots["titulo"].value
            ticket_description = handler_input.request_envelope.request.intent.slots["descricao"].value
            try:
                ticket_type = handler_input.request_envelope.request.intent.slots["tipo"].value
                ticket_type = (ticket_type == "incidente" and 1 or 2)
            except:
                ticket_type = 0
            
            data = {
                "ticket_name":ticket_name,
                "ticket_description":ticket_description,
                "ticket_type":ticket_type
            }
            
            
            # consulta na api
            retorno = vconnector_post("/alexa/tickets", data, handler_input)
            print(retorno)
            # if(retorno["status"] == "200"):
            #     speak_output = "Chamado criado com sucesso!"
            # else:
            #     speak_output = "Erro ao criar chamado!"
            if(retorno["message"] == "Ticket created successfully"):
                success_output = random.choice([
                    "Abertura de chamado de I. D {id} realizada com sucesso",
                    "Chamado de I. D {id} aberto com sucesso",
                    "Chamado de I. D {id} salvo com sucesso",
                    "Abertura de chamado de I. D {id} salva com sucesso"])
                success_output = success_output.format(id=retorno["result"])
                speak_output = success_output
            else:
                error_output = random.choice([
                    "Não foi possível realizar abertura do seu chamado!",
                    "A abertura do seu chamado não foi realizada!"])
                speak_output = error_output
        return (
            handler_input.response_builder
                .speak(speak_output).set_should_end_session(
            False)
                .response
        )


class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Olá, o que deseja fazer hoje?"
        
        #get_progressive_response(handler_input)
        return (
            handler_input.response_builder
                .speak(speak_output).set_should_end_session(
            False)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        if(str(exception) == "account_linking"):
            speak_output = "Você deve vincular sua conta. Por favor, acesse a página de configuração da Skill!"
        else:
            print(exception)
            print(str(exception))
            speak_output = "Hmm, algo deu errado!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )
class LogRequestInterceptor(AbstractRequestInterceptor):
    def process(self, handler_input):
        logger.info(f"Request type: {handler_input.request_envelope.request.object_type}")


sb = CustomSkillBuilder(api_client=DefaultApiClient())

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(VerificarConexaoBaseIntentHandler())
sb.add_request_handler(VincularDispositivoIntentHandler())
sb.add_request_handler(AberturaChamadoIntentHandler())


sb.add_exception_handler(CatchAllExceptionHandler())

sb.add_global_request_interceptor(LogRequestInterceptor())

lambda_handler = sb.lambda_handler()