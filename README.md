# Encurtaí

Encurte links, copie e compartilhe. Funciona localmente ou em uma hospedagem Python.

## Publicar no Render

A configuração `render.yaml` usa serviço pago e disco persistente para preservar o SQLite. Confira os valores no Render antes de confirmar a criação. Nada é contratado apenas por salvar estes arquivos.

1. Atualize no repositório https://github.com/Zancor1/Encurta- os arquivos `server.py`, `index.html`, `requirements.txt`, `render.yaml`, `.gitignore` e este README.
2. Não envie `.venv`, `.env` nem `links.sqlite3`. Se o banco já estiver no GitHub, remova-o do repositório; ele pode conter seus links locais.
3. Entre em https://dashboard.render.com e escolha **New > Blueprint**.
4. Conecte o GitHub e selecione o repositório **Zancor1/Encurta-**.
5. Confira o serviço, o plano e o disco definidos no `render.yaml`. Confirme apenas se concordar com os custos apresentados.
6. Aguarde o deploy terminar e abra a URL HTTPS fornecida pelo Render. Esse será o endereço para usar e compartilhar. GitHub Pages pode continuar desativado.

O servidor usa Flask com Waitress. A porta vem de `PORT`, e o banco de `DATABASE_PATH`. Na hospedagem ele escuta em `0.0.0.0`. O disco fica em `/var/data` e o banco em `/var/data/links.sqlite3`. O endpoint `/healthz` verifica a conexão com o banco.

A configuração inicia um banco novo na hospedagem. Não envia automaticamente seus links locais. Não troque de domínio depois de compartilhar links sem manter o domínio antigo funcionando.

Documentação: https://render.com/docs/infrastructure-as-code e https://render.com/docs/disks

## Rodar no computador

Requer Python 3.10 ou superior. No terminal, na pasta do projeto:

```cmd
python -m pip install -r requirements.txt
python server.py
```

Abra http://localhost:8000 e deixe o terminal aberto. Ctrl+C encerra o servidor. No Prompt de Comando, `cls` limpa a tela.

`localhost` aponta para seu computador. Links locais não abrem no computador de outra pessoa. Quando você acessar o site hospedado, a interface usará automaticamente o domínio público para criar os links.

## Histórico e banco

O histórico é público e mostra os 50 links mais recentes. Não há contas ou links privados. Não use para armazenar endereços confidenciais. O banco local é `links.sqlite3`; na hospedagem é usado o caminho configurado em `DATABASE_PATH`. Faça backups do banco na hospedagem.

## Testes

```cmd
python -m unittest discover -s tests -v
```
