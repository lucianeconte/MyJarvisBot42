"""
Baseado em:
https://khashtamov.com/en/how-to-create-a-telegram-bot-using-python/
"""

import json
from functools import partial

import telepot
from django.conf import settings
from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from myjarvisbot.jarvis.mixins import ListaMixin
from myjarvisbot.jarvis.models import ItensLista, UsersTelegram
from myjarvisbot.utils.semana_ano import get_semana_ano

TelegramBot = telepot.Bot(settings.TELEGRAM_BOT_TOKEN)


def _display_help():
    return render_to_string('help.md')


def _start(name, chat_id):
    UsersTelegram.objects.update_or_create(
        name=name,
        defaults={'chat_id': chat_id}
    )
    return _display_help()


def _insert_item_lista(data):
    produto = data.split(',')
    quantidade = '' if len(produto) < 2 else produto[1].strip()
    semana, ano = get_semana_ano()
    secao = ItensLista.OUTROS

    produto = produto[0].strip().title()

    ultimo_item_lista = ItensLista.objects.all().filter(produto=produto)
    ultimo_item_lista = ultimo_item_lista.order_by('-ano', '-semana')
    if ultimo_item_lista:
        secao = ultimo_item_lista.first().secao

    ItensLista.objects.update_or_create(
        produto=produto,
        semana=semana,
        ano=ano,
        defaults={'quantidade': quantidade,
                  'secao': secao},
    )
    return 'Ok, anotado!'


class CommandReceiveView(ListaMixin, View):
    def post(self, request, bot_token):
        if bot_token != settings.TELEGRAM_BOT_TOKEN:
            return HttpResponseForbidden('Invalid token')

        raw = request.body.decode('utf-8')

        try:
            payload = json.loads(raw)
        except ValueError:
            return HttpResponseBadRequest('Invalid request body')
        else:
            print(payload)
            chat_id = payload['message']['chat']['id']
            name = payload['message']['chat']['first_name']
            cmd = payload['message'].get('text')  # command

            msg = ' '.join(cmd.split()[1:])

            commands = {
                '/start': partial(_start, name=name, chat_id=chat_id),
                'help': _display_help,
                'lista': self.display_lista,
                'compra': partial(_insert_item_lista, data=msg),
                'comprar': partial(_insert_item_lista, data=msg),
            }

            func = commands.get(cmd.split()[0].lower())

            if func:
                TelegramBot.sendMessage(chat_id, func(), parse_mode='Markdown')
            else:
                TelegramBot.sendMessage(chat_id,
                                        'Desculpe! eu não entendi :-(')

        return JsonResponse({}, status=200)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CommandReceiveView, self).dispatch(request, *args, **kwargs)
