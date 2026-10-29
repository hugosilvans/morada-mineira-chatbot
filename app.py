from flask import Flask, request, jsonify, render_template, redirect, session, g
import os
import json
from urllib.parse import quote_plus
from datetime import datetime, timezone

from database import connect, init_db

app = Flask(__name__)
# Em hospedagem, SECRET_KEY deve ser estável e definida no ambiente.
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY") or os.urandom(32),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    MAX_CONTENT_LENGTH=100 * 1024,
)

COMPANY_WHATSAPP_NUMBER = "5561996393007"
COMPANY_WEBSITE = "https://www.moradamineira.com.br"


def get_db():
    """Uma conexão por requisição; teardown também cobre retornos de erro."""
    if "db" not in g:
        g.db = connect()
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


@app.before_request
def validar_json():
    """As rotas de escrita recebem objetos JSON, não listas ou valores soltos."""
    if request.path.startswith("/api/") and request.method == "POST":
        if not isinstance(request.get_json(), dict):
            return jsonify({"error": "JSON deve ser um objeto."}), 400


@app.before_request
def proteger_carrinho():
    # O ID informado pelo navegador não basta: o carrinho precisa ser da sessão.
    if request.endpoint not in {"api_add_to_cart", "api_cart", "api_remove_item", "api_checkout"}:
        return None
    cart_id = session.get("cart_id")
    if not cart_id:
        return jsonify({"error": "Crie um carrinho primeiro."}), 403
    if request.endpoint == "api_cart":
        informado = request.view_args["cart_id"]
    else:
        data = request.get_json() or {}
        if not isinstance(data, dict):
            return jsonify({"error": "JSON deve ser um objeto."}), 400
        informado = data.get("cart_id")
    if informado != cart_id:
        return jsonify({"error": "Carrinho não pertence à sessão."}), 403


def row_to_dict(row):
    return {k: row[k] for k in row.keys()}


@app.route("/")
def index():
    return render_template("index.html", company_website=COMPANY_WEBSITE)


@app.route("/api/menu")
def api_menu():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM menu_items")
    items = [row_to_dict(r) for r in cur.fetchall()]

    for it in items:
        cur.execute("SELECT id, `key`, type FROM option_groups WHERE menu_item_id = ?", (it["id"],))
        groups = [row_to_dict(g) for g in cur.fetchall()]
        opts_struct = {}
        for g in groups:
            cur.execute(
                "SELECT id, name, price_modifier FROM options WHERE option_group_id = ?", (g["id"],)
            )
            choices = []
            for o in cur.fetchall():
                oo = dict(o)
                choices.append({"id": oo["id"], "label": oo["name"], "extra": oo["price_modifier"]})
            opts_struct[g["key"]] = {"type": g["type"], "choices": choices}
        it["options"] = opts_struct

        it["bestseller"] = bool(it.get("bestseller"))
    conn.close()
    return jsonify({"menu": items})


@app.route("/api/categories")
def api_categories():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT DISTINCT category FROM menu_items WHERE category IS NOT NULL ORDER BY category"
    )
    categories = [row[0] for row in cur.fetchall()]
    conn.close()
    return jsonify({"categories": categories})


@app.route("/api/category/<category_name>")
def api_category(category_name):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM menu_items WHERE category = ?", (category_name,))
    items = [row_to_dict(r) for r in cur.fetchall()]

    for it in items:
        cur.execute("SELECT id, `key`, type FROM option_groups WHERE menu_item_id = ?", (it["id"],))
        groups = [row_to_dict(g) for g in cur.fetchall()]
        opts_struct = {}
        for g in groups:
            cur.execute(
                "SELECT id, name, price_modifier FROM options WHERE option_group_id = ?", (g["id"],)
            )
            choices = []
            for o in cur.fetchall():
                oo = dict(o)
                choices.append({"id": oo["id"], "label": oo["name"], "extra": oo["price_modifier"]})
            opts_struct[g["key"]] = {"type": g["type"], "choices": choices}
        it["options"] = opts_struct
        it["bestseller"] = bool(it.get("bestseller"))

    conn.close()
    return jsonify({"items": items, "category": category_name})


@app.route("/api/best_sellers")
def api_best_sellers():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """SELECT m.*, b.count FROM best_sellers b JOIN menu_items m ON b.menu_item_id = m.id ORDER BY b.count DESC LIMIT 10"""
    )
    items = []
    for r in cur.fetchall():
        row = row_to_dict(r)
        items.append(row)
    conn.close()
    return jsonify({"best_sellers": items})


@app.route("/api/best_sellers_categories")
def api_best_sellers_categories():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""SELECT DISTINCT m.category FROM best_sellers b 
                   JOIN menu_items m ON b.menu_item_id = m.id 
                   WHERE m.category IS NOT NULL ORDER BY m.category""")
    categories = [row[0] for row in cur.fetchall()]
    conn.close()
    return jsonify({"categories": categories})


@app.route("/api/best_sellers_category/<category_name>")
def api_best_sellers_category(category_name):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """SELECT m.*, b.count FROM best_sellers b 
                   JOIN menu_items m ON b.menu_item_id = m.id 
                   WHERE m.category = ? 
                   ORDER BY b.count DESC""",
        (category_name,),
    )
    items = []
    for r in cur.fetchall():
        row = row_to_dict(r)
        items.append(row)
    conn.close()
    return jsonify({"items": items, "category": category_name})


@app.route("/api/create_cart", methods=["POST"])
def api_create_cart():
    cart_id = os.urandom(16).hex()
    session["cart_id"] = cart_id
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO carts (id, created_at) VALUES (?,?)",
        (cart_id, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()
    return jsonify({"cart_id": cart_id})


@app.route("/api/add_to_cart", methods=["POST"])
def api_add_to_cart():
    data = request.get_json() or {}
    cart_id = data.get("cart_id")
    menu_item_id = data.get("menu_item_id")
    selected_options = data.get("selected_options", [])
    quantity = data.get("quantity", 1)
    if type(quantity) is not int or not 1 <= quantity <= 10000:
        return jsonify({"error": "Quantidade deve ser inteira entre 1 e 10000."}), 400
    if not isinstance(selected_options, list) or any(
        type(op) is not int for op in selected_options
    ):
        return jsonify({"error": "Opções inválidas."}), 400
    if len(selected_options) != len(set(selected_options)):
        return jsonify({"error": "Não repita IDs de opções."}), 400
    if not cart_id or not menu_item_id:
        return jsonify({"error": "cart_id and menu_item_id required"}), 400
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT base_price FROM menu_items WHERE id = ?", (menu_item_id,))
    row = cur.fetchone()
    if not row:
        return jsonify({"error": "menu item not found"}), 404
    base_price = row["base_price"]
    unit_price = base_price

    # Carregue as opções do produto, impedindo usar opções de outro item.
    cur.execute("SELECT id, type FROM option_groups WHERE menu_item_id = ?", (menu_item_id,))
    groups = cur.fetchall()
    cur.execute(
        "SELECT id, option_group_id, price_modifier FROM options WHERE menu_item_id = ?",
        (menu_item_id,),
    )
    options = {op["id"]: op for op in cur.fetchall()}
    if any(op not in options for op in selected_options):
        return jsonify({"error": "Opção não pertence ao produto."}), 400
    for group in groups:
        selected = [op for op in selected_options if options[op]["option_group_id"] == group["id"]]
        if not selected or (group["type"] == "single" and len(selected) != 1):
            return jsonify({"error": "Selecione as opções obrigatórias do produto."}), 400
    unit_price += sum(options[op]["price_modifier"] for op in selected_options)

    cur.execute(
        "INSERT INTO cart_items (cart_id, menu_item_id, selected_options, quantity, unit_price) VALUES (?,?,?,?,?)",
        (cart_id, menu_item_id, json.dumps(selected_options), quantity, unit_price),
    )

    cur.execute(
        "INSERT INTO best_sellers (menu_item_id, count) VALUES (?,?) ON CONFLICT(menu_item_id) DO UPDATE SET count = count + ?",
        (menu_item_id, quantity, quantity),
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})


@app.route("/api/cart/<cart_id>")
def api_cart(cart_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM cart_items WHERE cart_id = ?", (cart_id,))
    items = []
    for r in cur.fetchall():
        row = row_to_dict(r)

        cur.execute("SELECT name, description FROM menu_items WHERE id = ?", (row["menu_item_id"],))
        m = cur.fetchone()
        if m:
            row["menu_item_name"] = m["name"]
        row["selected_options"] = (
            json.loads(row["selected_options"]) if row["selected_options"] else []
        )
        items.append(row)
    conn.close()
    total = sum(i["unit_price"] * i["quantity"] for i in items)
    return jsonify({"items": items, "total": total})


@app.route("/api/remove_item", methods=["POST"])
def api_remove_item():
    data = request.get_json() or {}
    item_id = data.get("cart_item_id")
    if not item_id:
        return jsonify({"error": "cart_item_id required"}), 400
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM cart_items WHERE id = ? AND cart_id = ?", (item_id, session["cart_id"])
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})


@app.route("/api/suggestions", methods=["POST"])
def api_suggestions():
    data = request.get_json() or {}
    try:
        raw_qty = data.get("quantidade_de_pessoas", 1)
        if isinstance(raw_qty, bool) or not str(raw_qty).isdigit():
            raise ValueError
        qty = int(raw_qty)
        if not 1 <= qty <= 10000:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "Informe uma quantidade de pessoas válida."}), 400
    party_type = str(data.get("tipo_de_festa") or "").lower()
    location = data.get("localização") or ""

    conn = get_db()
    cur = conn.cursor()
    suggestions = []

    mapping = {
        "casamento": ["Tortas Especialidades", "Tortas", "Doces", "Bolos", "Bebidas"],
        "aniversário": ["Tortas Especialidades", "Tortas", "Bolos", "Doces"],
        "formal": ["Tortas Especialidades", "Salgados", "Bebidas"],
        "reunião": ["Salgados", "Bebidas", "Bolos"],
    }

    categories = mapping.get(party_type, mapping["aniversário"])

    discount = 0.0
    if qty > 50:
        discount = 0.10

    placeholders = ",".join("?" * len(categories))
    query = f"SELECT id, name, base_price, description, category FROM menu_items WHERE category IN ({placeholders}) ORDER BY bestseller DESC, name ASC"
    cur.execute(query, categories)
    items = [row_to_dict(r) for r in cur.fetchall()]

    for item in items:
        base_price = item["base_price"]
        est_total = 0.0

        if base_price == 0.0:

            if "Sanduíches" in item["name"] or "Salgados" in item["category"]:
                est_total = (qty / 25) * 40.0
            elif "Bombons" in item["name"] or "Doces" in item["category"]:
                est_total = (qty / 50) * 67.0
            elif "Bolo" in item["name"]:
                est_total = (qty / 10) * 45.0
            else:
                est_total = qty * 2.0
        else:

            if "Bebidas" in item["category"]:
                est_total = (qty / 5) * base_price
            else:
                est_total = base_price * max(1, qty // 10)

        est_discounted = est_total * (1 - discount)
        suggestions.append(
            {
                "id": item["id"],
                "name": item["name"],
                "category": item["category"],
                "estimate": round(est_discounted, 2),
                "discount_applied": discount > 0.0,
            }
        )

    conn.close()
    return jsonify({"sugestões": suggestions, "desconto": discount, "quantidade_de_pessoas": qty})


@app.route("/api/checkout", methods=["POST"])
def api_checkout():
    data = request.get_json() or {}
    cart_id = data.get("cart_id")
    if not cart_id:
        return jsonify({"error": "cart_id required"}), 400
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM cart_items WHERE cart_id = ?", (cart_id,))
    items = [row_to_dict(r) for r in cur.fetchall()]
    if not items:
        return jsonify({"erro": "carrinho vazio"}), 400

    lines = []
    total = 0.0
    for i in items:
        cur.execute("SELECT name FROM menu_items WHERE id = ?", (i["menu_item_id"],))
        m = cur.fetchone()
        name = m["name"] if m else ("item-" + str(i["menu_item_id"]))
        opts = json.loads(i["selected_options"]) if i["selected_options"] else []
        item_subtotal = i["unit_price"] * i["quantity"]

        # Formatação do item
        item_line = f"{i['quantity']} x {name:<30} R$ {item_subtotal:>7.2f}"
        lines.append(item_line)

        # Opções do item
        if opts:
            placeholders = ",".join("?" for _ in opts)
            cur.execute(f"SELECT name FROM options WHERE id IN ({placeholders})", opts)
            opt_names = [r["name"] for r in cur.fetchall()]
            options_str = ", ".join(opt_names)
            lines.append(f"     └─ {options_str}")

        total += item_subtotal

    # Formata o resumo como um recibo bonito
    separator = "=" * 55
    summary = f"\n{separator}\n"
    summary += "       PEDIDO - MORADA MINEIRA\n"
    summary += f"{separator}\n\n"
    summary += "Qtd | Produto                    | Valor\n"
    summary += "-" * 55 + "\n"
    summary += "\n".join(lines) + "\n\n"
    summary += "-" * 55 + "\n"
    summary += f"TOTAL{' ' * (55 - 18 - len(f'R$ {total:>7.2f}'))}R$ {total:>7.2f}\n"
    summary += f"{separator}\n"
    summary += "Obrigado pela sua compra!\n"
    summary += f"{separator}"
    conn.close()

    text = f"Novo pedido:\n{summary}"
    wa_msg = quote_plus(text)
    wa_link = f"https://api.whatsapp.com/send?phone={COMPANY_WHATSAPP_NUMBER}&text={wa_msg}"
    return jsonify({"whatsapp_link": wa_link, "resumo": summary})


@app.route("/support")
def support():
    return redirect(COMPANY_WEBSITE)


@app.route("/api/message", methods=["POST"])
def api_message():
    """Simple rule-based chatbot handling key intents: menu, carrinho, add, remover, sugestões, mais vendidos, suporte, finalizar."""
    data = request.get_json() or {}
    text = str(data.get("message") or "").lower()
    cart_id = data.get("cart_id")
    # Detect intents by keywords
    if any(k in text for k in ["menu", "mostrar menu", "ver menu", "show menu"]):
        return jsonify({"type": "menu", "text": "Aqui está o nosso menu.", "action": "open_menu"})
    if any(
        k in text for k in ["mais vendidos", "favoritos", "recomendados", "popular", "best sellers"]
    ):
        return jsonify(
            {
                "type": "mais_vendidos",
                "text": "Esses são os nossos favoritos.",
                "action": "open_best_sellers",
            }
        )
    if any(
        k in text for k in ["carrinho", "mostrar carrinho", "ver carrinho", "cart", "show cart"]
    ):
        return jsonify(
            {"type": "carrinho", "text": "Abrindo o seu carrinho.", "action": "open_cart"}
        )
    if any(k in text for k in ["add", "eu quero", "comprar", "pedir"]):
        return jsonify({"type": "add", "text": "Qual item você gostaria de adicionar?"})
    if any(k in text for k in ["sugestão", "sugestões", "não sei"]):
        return jsonify(
            {
                "type": "sugestões",
                "text": "Me diga a quantidade de pessoas, tipo de festa e localização.",
            }
        )
    if any(
        k in text for k in ["finalizar", "parar de comprar", "parar", "acabei", "só isso", "sair"]
    ):
        return jsonify(
            {
                "type": "finalizar",
                "text": "Pronto para finalizar. Seu pedido será mandado para o WhatsApp.",
            }
        )
    if any(k in text for k in ["suporte", "ajuda", "website", "support"]):
        return jsonify({"type": "suporte", "text": "Abrindo o site", "action": "open_support"})
    # default
    return jsonify(
        {
            "type": "não sei",
            "text": "Desculpa, eu não entendi. Você pode me pedir para mostrar o menu, carrinho, sugestões ou a finalização da sua compra.",
        }
    )


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
