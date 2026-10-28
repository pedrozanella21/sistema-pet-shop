# Sistema de Pet Shop 🐾

Sistema de gerenciamento de pet shop em Python, feito para rodar no terminal. Projeto da faculdade de Engenharia de Software.

## Funcionalidades

- Cadastro de tutores (dono do animal) e pets ligados a cada tutor
- Agendamento de serviços: banho, tosa, banho e tosa, consulta e vacina
- Bloqueia dois atendimentos no mesmo horário
- Agenda do dia com status (pendente ou concluído)
- Faturamento do dia, contando só os atendimentos concluídos
- Dados salvos em `petshop.json`

## Como rodar

Precisa do Python 3.8 ou mais novo. Não usa nenhuma biblioteca externa.

```bash
python petshop.py
```

## Exemplo

```
Agenda de 28/10/2026
[1] 09:00 ✔ banho e tosa  Thor (Ana Souza) R$ 100,00
[2] 14:30 … consulta      Mel (Carlos Lima) R$ 120,00
Faturado no dia: R$ 100,00
```

## Conceitos usados

- Programação orientada a objetos com várias classes que se relacionam (`Tutor`, `Pet`, `Agendamento`, `PetShop`)
- Manipulação de datas com `datetime`
- Validação de dados e tratamento de exceções
- Persistência em JSON
