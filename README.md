# Curto

Cole um endereço, clique em **Encurtar link** e copie o resultado. O site salva os links e conta quantas vezes cada um foi aberto.

## Rodar no computador

Você precisa do Python 3.10 ou mais recente. Não precisa instalar bibliotecas.

Na pasta do projeto, execute:

```cmd
python server.py
```

Abra http://localhost:8000 no navegador. Deixe o terminal aberto enquanto usa o site. Para parar, pressione Ctrl+C. No Prompt de Comando, `cls` limpa a tela.

## Por que localhost?

`localhost` aponta para o seu próprio computador. Esta versão roda nele. Se mandar um link com localhost para alguém, ele vai tentar abrir no computador dessa pessoa.

Para compartilhar os links, o servidor precisa ficar em uma hospedagem acessível pela internet. A interface já usa o endereço pelo qual foi aberta para montar os links curtos.

## Como colocar na internet

O projeto usa Python e SQLite. Precisa de uma hospedagem que execute o servidor e mantenha o banco salvo. Enviar só o HTML para uma hospedagem estática não faz o encurtador funcionar.

Um caminho é usar um Web Service no Render:

1. Coloque o projeto em um repositório no GitHub. Não envie o arquivo `links.sqlite3`.
2. Adapte o servidor para produção, por exemplo com Flask e Gunicorn. O servidor atual usa `http.server` para desenvolvimento e escuta só em `127.0.0.1`. Na hospedagem, precisa escutar em `0.0.0.0` e na porta da variável `PORT`.
3. Conecte o repositório ao Render e crie um Web Service Python.
4. Configure um disco persistente e adapte o caminho do SQLite para usar esse disco. No Render, isso exige um serviço pago. Sem persistência, os links podem sumir quando o serviço reiniciar ou for atualizado. Outra opção é adaptar o projeto para um banco externo.
5. Depois de publicar, use o endereço HTTPS fornecido pela hospedagem. Um domínio próprio é opcional.

Os ajustes de produção acima ainda não estão implementados. O projeto atual é a versão local.

Documentação: https://render.com/docs/web-services e https://render.com/docs/disks

## Dados salvos

O banco fica em `links.sqlite3`. O histórico mostra até 50 links recentes e é compartilhado entre todos os visitantes. Não existem contas ou histórico privado nesta versão. Se quiser links privados em um site público, esse comportamento precisa mudar antes de publicar.
