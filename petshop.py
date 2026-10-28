"""Sistema de Gerenciamento de Pet Shop (linha de comando).

Cadastro de tutores e pets, agendamento de serviços (banho, tosa,
consulta) com controle de horário, e resumo do faturamento do dia.
Os dados ficam salvos em um arquivo JSON.
"""

import json
from datetime import datetime
from pathlib import Path

ARQUIVO = Path(__file__).with_name("petshop.json")

SERVICOS = {
    "banho": 50.00,
    "tosa": 70.00,
    "banho e tosa": 100.00,
    "consulta": 120.00,
    "vacina": 90.00,
}


class Tutor:
    def __init__(self, id, nome, telefone):
        self.id = id
        self.nome = nome
        self.telefone = telefone


class Pet:
    def __init__(self, id, nome, especie, raca, tutor_id):
        self.id = id
        self.nome = nome
        self.especie = especie
        self.raca = raca
        self.tutor_id = tutor_id


class Agendamento:
    def __init__(self, id, pet_id, servico, data_hora, preco, concluido=False):
        self.id = id
        self.pet_id = pet_id
        self.servico = servico
        self.data_hora = data_hora  # formato "dd/mm/aaaa hh:mm"
        self.preco = float(preco)
        self.concluido = concluido

    @property
    def quando(self):
        return datetime.strptime(self.data_hora, "%d/%m/%Y %H:%M")


class PetShop:
    def __init__(self, arquivo=ARQUIVO):
        self.arquivo = Path(arquivo)
        self.tutores, self.pets, self.agendamentos = {}, {}, {}
        self.carregar()

    # ---------- persistência ----------
    def carregar(self):
        if not self.arquivo.exists():
            return
        d = json.loads(self.arquivo.read_text(encoding="utf-8"))
        self.tutores = {t["id"]: Tutor(**t) for t in d.get("tutores", [])}
        self.pets = {p["id"]: Pet(**p) for p in d.get("pets", [])}
        self.agendamentos = {a["id"]: Agendamento(**a) for a in d.get("agendamentos", [])}

    def salvar(self):
        d = {
            "tutores": [vars(t) for t in self.tutores.values()],
            "pets": [vars(p) for p in self.pets.values()],
            "agendamentos": [vars(a) for a in self.agendamentos.values()],
        }
        self.arquivo.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def _proximo_id(colecao):
        return max(colecao, default=0) + 1

    # ---------- cadastros ----------
    def cadastrar_tutor(self, nome, telefone):
        if not nome:
            raise ValueError("Informe o nome do tutor.")
        tutor = Tutor(self._proximo_id(self.tutores), nome, telefone)
        self.tutores[tutor.id] = tutor
        self.salvar()
        return tutor

    def cadastrar_pet(self, nome, especie, raca, tutor_id):
        if tutor_id not in self.tutores:
            raise KeyError("Tutor não encontrado.")
        pet = Pet(self._proximo_id(self.pets), nome, especie, raca, tutor_id)
        self.pets[pet.id] = pet
        self.salvar()
        return pet

    # ---------- agenda ----------
    def agendar(self, pet_id, servico, data_hora):
        if pet_id not in self.pets:
            raise KeyError("Pet não encontrado.")
        servico = servico.lower()
        if servico not in SERVICOS:
            raise ValueError(f"Serviço inválido. Opções: {', '.join(SERVICOS)}.")
        try:
            quando = datetime.strptime(data_hora, "%d/%m/%Y %H:%M")
        except ValueError:
            raise ValueError("Data inválida. Use o formato dd/mm/aaaa hh:mm.")
        if any(a.quando == quando and not a.concluido for a in self.agendamentos.values()):
            raise ValueError("Já existe um atendimento nesse horário.")
        ag = Agendamento(self._proximo_id(self.agendamentos), pet_id, servico,
                         data_hora, SERVICOS[servico])
        self.agendamentos[ag.id] = ag
        self.salvar()
        return ag

    def concluir(self, agendamento_id):
        ag = self.agendamentos.get(agendamento_id)
        if ag is None:
            raise KeyError("Agendamento não encontrado.")
        ag.concluido = True
        self.salvar()

    def agenda_do_dia(self, dia):
        return sorted((a for a in self.agendamentos.values() if a.quando.date() == dia),
                      key=lambda a: a.quando)

    def faturamento(self, dia):
        return sum(a.preco for a in self.agenda_do_dia(dia) if a.concluido)


# ---------- interface no terminal ----------
def moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pedir(texto):
    return input(texto).strip()


def pedir_id(texto):
    valor = pedir(texto)
    if not valor.isdigit():
        raise ValueError("Digite um número.")
    return int(valor)


def mostrar_agenda(loja, dia):
    agenda = loja.agenda_do_dia(dia)
    print(f"\nAgenda de {dia.strftime('%d/%m/%Y')}")
    if not agenda:
        print("Nenhum atendimento.")
    for a in agenda:
        pet = loja.pets[a.pet_id]
        tutor = loja.tutores[pet.tutor_id]
        status = "✔" if a.concluido else "…"
        print(f"[{a.id}] {a.quando:%H:%M} {status} {a.servico:<13} {pet.nome} ({tutor.nome}) {moeda(a.preco)}")
    print(f"Faturado no dia: {moeda(loja.faturamento(dia))}")


def menu():
    loja = PetShop()
    opcoes = {
        "1": "Cadastrar tutor",
        "2": "Cadastrar pet",
        "3": "Listar tutores e pets",
        "4": "Agendar serviço",
        "5": "Agenda de hoje",
        "6": "Concluir atendimento",
        "7": "Tabela de preços",
        "0": "Sair",
    }
    while True:
        print("\n===== PET SHOP =====")
        for chave, texto in opcoes.items():
            print(f"[{chave}] {texto}")
        escolha = pedir("Escolha: ")
        try:
            if escolha == "1":
                t = loja.cadastrar_tutor(pedir("Nome: "), pedir("Telefone: "))
                print(f"Tutor cadastrado com ID {t.id}.")
            elif escolha == "2":
                p = loja.cadastrar_pet(pedir("Nome do pet: "), pedir("Espécie: "),
                                       pedir("Raça: "), pedir_id("ID do tutor: "))
                print(f"Pet cadastrado com ID {p.id}.")
            elif escolha == "3":
                if not loja.tutores:
                    print("\nNenhum tutor cadastrado.")
                for t in loja.tutores.values():
                    print(f"\n[{t.id}] {t.nome} - {t.telefone}")
                    for p in loja.pets.values():
                        if p.tutor_id == t.id:
                            print(f"    pet [{p.id}] {p.nome} ({p.especie}, {p.raca})")
            elif escolha == "4":
                ag = loja.agendar(pedir_id("ID do pet: "), pedir("Serviço: "),
                                  pedir("Data e hora (dd/mm/aaaa hh:mm): "))
                print(f"Agendado! {ag.servico} em {ag.data_hora} - {moeda(ag.preco)}")
            elif escolha == "5":
                mostrar_agenda(loja, datetime.now().date())
            elif escolha == "6":
                loja.concluir(pedir_id("ID do agendamento: "))
                print("Atendimento concluído.")
            elif escolha == "7":
                for nome, preco in SERVICOS.items():
                    print(f"{nome:<14}{moeda(preco)}")
            elif escolha == "0":
                print("Até mais!")
                break
            else:
                print("Opção inválida.")
        except (ValueError, KeyError) as erro:
            print(f"Erro: {erro.args[0]}")


if __name__ == "__main__":
    menu()
