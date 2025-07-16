# Project Step by Step 

## Configurando o ambiente - Setting up the environment

```
python -m venv venv
cd venv\scripts
activate

```
press ctrl+shift+p: Python: Select Interpreter

e selecione o interpretador do venv

flet create flet

//primeiro teste

```
flet run aula.py

flet run aula.py -w

```

// coleta

```
pip install reportlab

```

Para verificar quantas bibliotecas estão instaladas no seu ambiente virtual (venv) e gerar um arquivo requirements.txt, siga estes passos:

1. Ative seu ambiente virtual:

# No Windows:
.\venv\Scripts\activate

# No Linux/Mac:
source venv/bin/activate

2. Liste todas as bibliotecas instaladas e conte quantas são:
pip list

Para contar quantas bibliotecas estão instaladas:
pip list | wc -l  # Linux/Mac
pip list | measure | select -expand Count  # Windows PowerShell

3. Gerar o arquivo requirements.txt:
pip freeze > requirements.txt

4. Verifique o conteúdo do arquivo gerado:
cat requirements.txt  # Linux/Mac
type requirements.txt  # Windows

instalar
pip install -r requirements.txt 