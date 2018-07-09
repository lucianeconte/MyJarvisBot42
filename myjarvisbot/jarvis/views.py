import json
import telepot
from django.template.loader import render_to_string
from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings

from myjarvisbot.jarvis.models import ItensLista


TelegramBot = telepot.Bot(settings.TELEGRAM_BOT_TOKEN)

def _display_help():
    return render_to_string('help.md')


def _insert_item_lista(command):
    produto = command.split(',')
    quantidade = '' if len(produto) < 2 else produto[1].strip()
    obj = ItensLista(produto=produto[0], quantidade=quantidade)
    obj.save()

def _display_lista():
    return render_to_string('lista.md', {'items': ItensLista.objects.all()})
    # itens = []
    # for item in ItensLista.objects.all():
    #     quantide = '' if item.quantidade == '' else ', {}'.format(item.quantidade)
    #     itens.append('{}, {}'.format(item.produto, quantide))
    # return '\n'.join(itens)


class CommandReceiveView(View):
    def post(self, request, bot_token):
        if bot_token != settings.TELEGRAM_BOT_TOKEN:
            return HttpResponseForbidden('Invalid token')

        commands = {
            '/start': _display_help,
            'help': _display_help,
            'lista': _display_lista,
        }

        raw = request.body.decode('utf-8')

        try:
            payload = json.loads(raw)
        except ValueError:
            return HttpResponseBadRequest('Invalid request body')
        else:
            chat_id = payload['message']['chat']['id']
            cmd = payload['message'].get('text')  # command

            func = commands.get(cmd.split()[0].lower())
            if func:
                TelegramBot.sendMessage(chat_id, func(), parse_mode='Markdown')
            elif cmd.split()[0].strip().lower()[:6] == 'compra':
                TelegramBot.sendMessage(chat_id, 'Ok')
                _insert_item_lista(''.join(cmd.split()[1:]))
                #_insert_item_lista('Tomate, 1kg')
                TelegramBot.sendMessage(chat_id, 'Anotado!')
            else:
                TelegramBot.sendMessage(chat_id,
                                        'I do not understand you, Sir!')

        return JsonResponse({}, status=200)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CommandReceiveView, self).dispatch(request, *args, **kwargs)
