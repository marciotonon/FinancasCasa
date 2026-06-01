from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
from datetime import datetime, date
from collections import defaultdict

app = Flask(__name__)
DATA_FILE = "data.json"

MONTH_NAMES = {
    "01": "Janeiro",
    "02": "Fevereiro",
    "03": "Marco",
    "04": "Abril",
    "05": "Maio",
    "06": "Junho",
    "07": "Julho",
    "08": "Agosto",
    "09": "Setembro",
    "10": "Outubro",
    "11": "Novembro",
    "12": "Dezembro",
}

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"transacoes": [], "contas": [], "categorias": ["Alimentação", "Moradia", "Transporte", "Saúde", "Educação", "Lazer", "Salário", "Outros"]}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def group_contas_by_month(contas):
    grupos = []
    grupo_atual = None

    for conta in contas:
        ano, mes, _ = conta["vencimento"].split("-")
        chave_mes = f"{ano}-{mes}"

        if not grupo_atual or grupo_atual["chave"] != chave_mes:
            grupo_atual = {
                "chave": chave_mes,
                "titulo": f"{MONTH_NAMES.get(mes, mes)} de {ano}",
                "contas": [],
            }
            grupos.append(grupo_atual)

        grupo_atual["contas"].append(conta)

    return grupos

def group_transacoes_by_month(transacoes):
    grupos = []
    grupo_atual = None

    for transacao in transacoes:
        ano, mes, _ = transacao["data"].split("-")
        chave_mes = f"{ano}-{mes}"

        if not grupo_atual or grupo_atual["chave"] != chave_mes:
            grupo_atual = {
                "chave": chave_mes,
                "titulo": f"{MONTH_NAMES.get(mes, mes)} de {ano}",
                "transacoes": [],
                "entradas": 0,
                "saidas": 0,
                "saldo": 0,
            }
            grupos.append(grupo_atual)

        grupo_atual["transacoes"].append(transacao)
        if transacao["tipo"] == "entrada":
            grupo_atual["entradas"] += transacao["valor"]
        else:
            grupo_atual["saidas"] += transacao["valor"]
        grupo_atual["saldo"] = grupo_atual["entradas"] - grupo_atual["saidas"]

    return grupos

def get_resumo(data):
    entradas = sum(t["valor"] for t in data["transacoes"] if t["tipo"] == "entrada" and not t.get("cancelado"))
    saidas = sum(t["valor"] for t in data["transacoes"] if t["tipo"] == "saida" and not t.get("cancelado"))
    contas_pendentes = [c for c in data["contas"] if c["status"] == "pendente"]
    total_pendente = sum(c["valor"] for c in contas_pendentes)
    return {
        "entradas": entradas,
        "saidas": saidas,
        "saldo": entradas - saidas,
        "total_pendente": total_pendente,
        "contas_pendentes": len(contas_pendentes)
    }

@app.route("/")
def index():
    data = load_data()
    resumo = get_resumo(data)
    transacoes = sorted(data["transacoes"], key=lambda x: x["data"], reverse=True)[:10]
    contas_pendentes = [c for c in data["contas"] if c["status"] == "pendente"]
    contas_pendentes.sort(key=lambda x: x["vencimento"])
    hoje = date.today().isoformat()
    return render_template("index.html", resumo=resumo, transacoes=transacoes, contas_pendentes=contas_pendentes, hoje=hoje)

@app.route("/transacoes")
def transacoes():
    data = load_data()
    filtro_tipo = request.args.get("tipo", "")
    filtro_mes = request.args.get("mes", "")
    filtro_categoria = request.args.get("categoria", "")
    lista = data["transacoes"]
    if filtro_tipo:
        lista = [t for t in lista if t["tipo"] == filtro_tipo]
    if filtro_mes:
        lista = [t for t in lista if t["data"].startswith(filtro_mes)]
    if filtro_categoria:
        lista = [t for t in lista if t.get("categoria") == filtro_categoria]
    lista = sorted(lista, key=lambda x: x["data"], reverse=True)
    transacoes_por_mes = group_transacoes_by_month(lista)
    resumo = get_resumo(data)
    return render_template(
        "transacoes.html",
        transacoes=lista,
        transacoes_por_mes=transacoes_por_mes,
        categorias=data["categorias"],
        filtro_tipo=filtro_tipo,
        filtro_mes=filtro_mes,
        filtro_categoria=filtro_categoria,
        resumo=resumo,
    )

@app.route("/transacoes/nova", methods=["GET", "POST"])
def nova_transacao():
    data = load_data()
    if request.method == "POST":
        transacao = {
            "id": int(datetime.now().timestamp() * 1000),
            "descricao": request.form["descricao"],
            "valor": float(request.form["valor"]),
            "tipo": request.form["tipo"],
            "categoria": request.form["categoria"],
            "data": request.form["data"],
            "observacao": request.form.get("observacao", ""),
            "cancelado": False
        }
        data["transacoes"].append(transacao)
        save_data(data)
        return redirect(url_for("transacoes"))
    return render_template("form_transacao.html", categorias=data["categorias"], hoje=date.today().isoformat())

@app.route("/transacoes/excluir/<int:tid>", methods=["POST"])
def excluir_transacao(tid):
    data = load_data()
    data["transacoes"] = [t for t in data["transacoes"] if t["id"] != tid]
    save_data(data)
    return redirect(url_for("transacoes"))

@app.route("/contas")
def contas():
    data = load_data()
    filtro_status = request.args.get("status", "")
    filtro_mes = request.args.get("mes", "")
    lista = data["contas"]
    if filtro_status:
        lista = [c for c in lista if c["status"] == filtro_status]
    if filtro_mes:
        lista = [c for c in lista if c["vencimento"].startswith(filtro_mes)]
    lista = sorted(lista, key=lambda x: x["vencimento"])
    contas_por_mes = group_contas_by_month(lista)
    hoje = date.today().isoformat()
    return render_template(
        "contas.html",
        contas=lista,
        contas_por_mes=contas_por_mes,
        filtro_status=filtro_status,
        filtro_mes=filtro_mes,
        hoje=hoje,
        categorias=data["categorias"],
    )

@app.route("/contas/nova", methods=["GET", "POST"])
def nova_conta():
    data = load_data()
    if request.method == "POST":
        conta = {
            "id": int(datetime.now().timestamp() * 1000),
            "descricao": request.form["descricao"],
            "valor": float(request.form["valor"]),
            "vencimento": request.form["vencimento"],
            "categoria": request.form["categoria"],
            "status": "pendente",
            "observacao": request.form.get("observacao", ""),
            "recorrente": request.form.get("recorrente") == "on"
        }
        data["contas"].append(conta)
        save_data(data)
        return redirect(url_for("contas"))
    return render_template("form_conta.html", categorias=data["categorias"], hoje=date.today().isoformat())

@app.route("/contas/baixar/<int:cid>", methods=["POST"])
def baixar_conta(cid):
    data = load_data()
    data_pagamento = request.form.get("data_pagamento") or date.today().isoformat()
    origem = request.form.get("origem", "contas")
    for conta in data["contas"]:
        if conta["id"] == cid:
            conta["status"] = "pago"
            conta["data_pagamento"] = data_pagamento
            transacao = {
                "id": int(datetime.now().timestamp() * 1000),
                "descricao": f"Pagamento: {conta['descricao']}",
                "valor": conta["valor"],
                "tipo": "saida",
                "categoria": conta.get("categoria", "Outros"),
                "data": data_pagamento,
                "observacao": f"Baixa automática da conta #{cid}",
                "cancelado": False
            }
            data["transacoes"].append(transacao)
            break
    save_data(data)
    return redirect(url_for(origem))

@app.route("/contas/excluir/<int:cid>", methods=["POST"])
def excluir_conta(cid):
    data = load_data()
    data["contas"] = [c for c in data["contas"] if c["id"] != cid]
    save_data(data)
    return redirect(url_for("contas"))

@app.route("/relatorios")
def relatorios():
    data = load_data()
    # Agrupa por mês
    por_mes = defaultdict(lambda: {"entradas": 0, "saidas": 0})
    for t in data["transacoes"]:
        if t.get("cancelado"):
            continue
        mes = t["data"][:7]
        if t["tipo"] == "entrada":
            por_mes[mes]["entradas"] += t["valor"]
        else:
            por_mes[mes]["saidas"] += t["valor"]
    meses = sorted(por_mes.keys(), reverse=True)[:12]
    dados_meses = [{"mes": m, **por_mes[m], "saldo": por_mes[m]["entradas"] - por_mes[m]["saidas"]} for m in meses]
    # Agrupa por categoria
    por_categoria = defaultdict(float)
    for t in data["transacoes"]:
        if t.get("cancelado") or t["tipo"] != "saida":
            continue
        por_categoria[t.get("categoria", "Outros")] += t["valor"]
    categorias_data = [{"categoria": k, "total": v} for k, v in sorted(por_categoria.items(), key=lambda x: -x[1])]
    resumo = get_resumo(data)
    return render_template("relatorios.html", dados_meses=dados_meses, categorias_data=categorias_data, resumo=resumo)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
