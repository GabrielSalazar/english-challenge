# English Challenge · página pública

Cópia só de leitura do rastreador do desafio de inglês de 60 dias (1/out a 1/dez/2026),
publicada no Vercel. O rastreador original, onde as respostas são feitas, é um artifact no Claude.

## Estrutura

- `src/tracker.html`: código do rastreador (o mesmo do artifact). Em modo estático
  (`window.__STATIC__`), lê `data.json` e mostra tudo em modo leitura.
- `scripts/build.py`: gera `public/index.html`, `public/data.json` e copia os áudios para `public/audio/`.
- `public/`: o que o Vercel publica (`vercel.json` aponta para essa pasta, sem build).

## Atualizar

1. Exportar a coleção `days` do artifact para uma pasta (um JSON por dia).
2. Baixar os áudios novos (cada um nomeado `<id do asset>.<ext>`) para outra pasta.
3. `python3 scripts/build.py --db <pasta dos dias> --audio <pasta dos áudios>`
4. Commit e push em `main`: o Vercel publica sozinho.
