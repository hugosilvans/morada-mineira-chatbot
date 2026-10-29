"""Regressões HTTP com SQLite temporário; não altera o banco versionado."""

import tempfile
import unittest
import os
import database
from app import app


class CarrinhoTest(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        database.DB_PATH = os.path.join(self.pasta.name, "teste.sqlite")
        database.init_db()
        app.config.update(TESTING=True, SECRET_KEY="chave-apenas-do-teste")
        self.cliente = app.test_client()
        self.cart_id = self.cliente.post("/api/create_cart", json={}).get_json()["cart_id"]

    def tearDown(self):
        self.pasta.cleanup()

    def test_quantidade_e_propriedade(self):
        dados = {"cart_id": self.cart_id, "menu_item_id": 30, "quantity": -1}
        self.assertEqual(self.cliente.post("/api/add_to_cart", json=dados).status_code, 400)
        outro = app.test_client()
        self.assertEqual(outro.get("/api/cart/" + self.cart_id).status_code, 403)
        dados["quantity"] = 1
        self.assertEqual(self.cliente.post("/api/add_to_cart", json=dados).status_code, 200)
        resposta = self.cliente.post("/api/checkout", json={"cart_id": self.cart_id})
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("resumo", resposta.get_json())

    def test_opcoes_e_remocao(self):
        dados = {
            "cart_id": self.cart_id,
            "menu_item_id": 30,
            "quantity": 1,
            "selected_options": [1],
        }
        self.assertEqual(self.cliente.post("/api/add_to_cart", json=dados).status_code, 400)
        dados["selected_options"] = []
        self.cliente.post("/api/add_to_cart", json=dados)
        item = self.cliente.get("/api/cart/" + self.cart_id).get_json()["items"][0]
        outro = app.test_client()
        outro_id = outro.post("/api/create_cart", json={}).get_json()["cart_id"]
        outro.post("/api/remove_item", json={"cart_id": outro_id, "cart_item_id": item["id"]})
        self.assertEqual(len(self.cliente.get("/api/cart/" + self.cart_id).get_json()["items"]), 1)

    def test_sugestao_invalida(self):
        for quantidade in ["abc", -5, 0, 1.5, True]:
            self.assertEqual(
                self.cliente.post(
                    "/api/suggestions", json={"quantidade_de_pessoas": quantidade}
                ).status_code,
                400,
            )


if __name__ == "__main__":
    unittest.main()
