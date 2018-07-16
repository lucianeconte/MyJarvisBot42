from django.test import TestCase

from myjarvisbot.jarvis import views
from myjarvisbot.jarvis.models import ItensLista, UsersTelegram



class TestInsertItemListaComQuantide(TestCase):
    def setUp(self):
        views._insert_item_lista(data='tomate, 1kg')

    def test_insert_item_descricao(self):
        self.assertEqual(ItensLista.objects.all()[0].produto, 'Tomate')

    def test_insert_item_quantidade(self):
        self.assertEqual(ItensLista.objects.all()[0].quantidade, '1kg')


class TestInsertItemListaSemQuantide(TestCase):
    def setUp(self):
        views._insert_item_lista(data='tomate')

    def test_insert_item_descricao(self):
        self.assertEqual(ItensLista.objects.all()[0].produto, 'Tomate')

    def test_insert_item_quantidade(self):
        self.assertEqual(ItensLista.objects.all()[0].quantidade, '')


class TestInsertItemListaProdutoComEspaco(TestCase):
    def setUp(self):
        views._insert_item_lista(data='Coco Ralado')

    def test_insert_item_descricao_com_espaco(self):
        self.assertEqual(ItensLista.objects.all()[0].produto, 'Coco Ralado')


class TestInsertProdutosRepetidos(TestCase):
    def setUp(self):
        views._insert_item_lista(data='Linguicinha, 1')
        views._insert_item_lista(data='Linguicinha, 2')

    def test_se_existe_apenas_1(self):
        self.assertEqual(len(ItensLista.objects.all()), 1)

    def test_se_atualizou_para_ultimo(self):
        self.assertEqual(ItensLista.objects.all()[0].quantidade, '2')


class TestLista(TestCase):
    def setUp(self):
        self.obj = ItensLista.objects.bulk_create([
            ItensLista(produto='Tomate', secao=ItensLista.HORTIFRUTI),
            ItensLista(produto='Cebola', secao=ItensLista.HORTIFRUTI),
            ItensLista(produto='Batatinha', secao=ItensLista.HORTIFRUTI),
            ItensLista(produto='Carne Moida', secao=ItensLista.CARNES,
                       quantidade='2'),
        ])

    def test_retorno_lista(self):
        expected = '\n\n*HORTIFRUTI*\n - Tomate\n - Cebola\n - Batatinha\n\n*CARNES*\n - Carne Moida 2\n'
        self.assertEqual(views._display_lista(), expected)


class TestStart(TestCase):
    def setUp(self):
        views._start('eliezerfb', '123')
        views._start('eliezerfb', '321')

    def test_start_exists(self):
        self.assertTrue(UsersTelegram.objects.exists())

    def test_start_update(self):
        self.assertEqual(UsersTelegram.objects.all()[0].chat_id, '321')


class TestBuscaUltimaSecao(TestCase):
    def test_ultima_secao(self):
        """Testa se o item inserido utiliza a última seção utilizada"""
        self.obj = ItensLista.objects.bulk_create([
            ItensLista(produto='Tomate', secao=ItensLista.CARNES,
                       ano=2018, semana=1),
            ItensLista(produto='Tomate', secao=ItensLista.HORTIFRUTI,
                       ano=2018, semana=2),
        ])
        views._insert_item_lista(data='Tomate')
        self.assertEqual(ItensLista.objects.all()[1].secao,
                         ItensLista.objects.all()[2].secao)
