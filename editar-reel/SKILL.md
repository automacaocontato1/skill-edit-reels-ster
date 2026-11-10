---
name: editar-reel
description: Edita reel falado (Instagram, TikTok, Shorts) direto no computador. Transcreve localmente, corta pausas e erros com aprovação, junta vários vídeos, alterna tela cheia, tela dividida e só gráficos conforme o conteúdo, põe legenda da fala com palavra-chave em destaque, manchete, prints anotados, cartões, sons e transições, segue receitas e referências de estilo e exporta em 9:16. Use quando pedirem "edita esse vídeo", "faz o reel", "junta esses vídeos", "corta as pausas", "coloca legenda", "divide a tela", "coloca o print", "põe um efeito sonoro", "usa esse estilo", "cria uma receita dessa referência", "configura minha identidade visual", "muda meu estilo" ou chamarem /editar-reel.
---

# Editar reel

Você edita reels falados. A pessoa grava falando para a câmera e você entrega o vídeo cortado, com ritmo, com o visual decidido trecho a trecho e pronto para postar. A transcrição roda no computador dela, nada vai para a internet.

## Como rodar os comandos

Todos os comandos usam o Python da pasta `.venv` que o instalador cria dentro desta skill:
- Mac e Linux: `<pasta da skill>/.venv/bin/python <pasta da skill>/motor/cli.py COMANDO`
- Windows: `<pasta da skill>\.venv\Scripts\python.exe <pasta da skill>\motor\cli.py COMANDO`

Abaixo, `reel` significa essa linha inteira. Caminhos com espaço vão entre aspas.

Na primeira vez, rode `reel checar`. Se faltar algo, rode o instalador do repositório ou siga o que o comando indicar. Se ele avisar que a identidade visual não está configurada, comece pela etapa 0.

## Organização de arquivos que a pessoa pode usar

Quando a pessoa indicar uma pasta, procure nela:
```
meu-reel/
├── videos/       01-abertura.mov, 02-demonstracao.mov ...   (a ordem dos nomes é a ordem da edição)
├── imagens/      prints, logos, ilustrações (também vale prints/ e ilustracoes/)
├── sons/         pop.wav, whoosh.mp3 ...
└── estilo/       referencia.png, MinhaFonte-Bold.ttf, cores.md ...   (opcional)
```
- Liste a pasta antes de qualquer coisa e mostre o que encontrou.
- Vídeos numerados (01, 02...) seguem essa ordem. Sem número, pergunte a ordem.
- Imagens e sons: associe cada arquivo ao momento que a pessoa descreveu. Se o nome não deixar claro qual é qual, pergunte.
- Se a pessoa disser a ordem em texto, a ordem dela vale mais que o nome do arquivo.

## Fluxo

### 0. Identidade visual (primeira vez)
Leia o `estilo-padrao.json` desta skill. Faça esta etapa antes de editar enquanto ele tiver `"_configurado": false`, e também quando a pessoa pedir "configura minha identidade visual" ou "muda meu estilo". Sem a chave `_configurado`, a identidade já está configurada (instalação antiga): siga para o passo 1.

Diga em uma linha que, antes do primeiro vídeo, vai aprender o visual dela e que isso acontece uma vez só, ou que, se ela preferir, segue com o visual padrão da skill (verdes e dourado) e ela configura depois. Se a identidade já existe ("muda meu estilo"), mostre antes o que está salvo e aceite "mantém" em qualquer pergunta.

**Se a pessoa preferir o padrão** ("pula", "usa o padrão", "depois eu vejo"): grave só `"_configurado": true` no `estilo-padrao.json`, sem mudar mais nada e sem criar receita nem `identidade.md`. Diga em uma linha que seguiu com o visual padrão e que ela pode pedir "configura minha identidade visual" quando quiser. Siga para o passo 1.

**Perguntas**, uma por vez, nesta ordem. Qualquer uma pode ficar sem resposta: o que ficar vazio continua como está.
1. **Referências visuais.** Imagens do feed, posts, logo, paleta, capas ou vídeos dela. Ela pode arrastar os arquivos para o terminal ou indicar uma pasta.
2. **Cores.** Principal, destaque, fundo claro e fundo escuro. Vale hex, nome da cor ("verde-musgo") ou "tira das imagens".
3. **Fontes.** O nome da fonte, o arquivo `.ttf`/`.otf` ou "não sei".
4. **Composição.** Legenda com caixa atrás ou solta; em maiúsculas ou não; fundo claro ou escuro na maior parte do vídeo; ritmo calmo ou dinâmico.
5. **O que evitar.** Cores, fontes, efeitos ou formatos que ela não quer ver.

**Análise das referências**
- Cores: `reel estilo ARQUIVO_OU_PASTA [...]` mede as cores dominantes de cada imagem e lê os hex de arquivos `.txt` e `.md`.
- Vídeo: `reel referencia VIDEO` gera as folhas de quadros. Abra as folhas e passe a pasta delas para o `reel estilo` (ignore o cinza da moldura e o vermelho da marca de tempo).
- Abra cada imagem e anote o que a cor não mede: peso da fonte (fina, regular, negrito, extra negrito), caixa atrás do texto (cor e transparência), cantos (retos, arredondados, pílula), espaçamento (justo ou arejado), contraste (forte ou suave) e posição do texto (topo, centro, terço de baixo).
- Nome de cor: escolha o tom e mostre o hex.
- Fonte vista numa imagem: diga qual fonte livre (licença OFL) é a mais parecida no desenho e avise que é uma aproximação. Se ela não vier com a skill (Montserrat, Playfair Display, DM Sans), peça o arquivo, que a pessoa baixa em fonts.google.com. Fonte paga só entra com o arquivo que a pessoa já tem; nunca procure nem baixe fonte paga.
- Arquivo de fonte: copie para a pasta `fontes/` desta skill (o instalador mantém as fontes acrescentadas) e use o nome do arquivo, sem a extensão, na chave. Com vários pesos da mesma família, use o mais forte (ExtraBold ou Bold) em `fonte`.

**Como as respostas viram estilo**

| Resposta | Onde entra |
|---|---|
| destaque | `cor_destaque` (palavra-chave sobre fundo escuro e sobre o vídeo) |
| principal | `cor_destaque_claro` (palavra-chave sobre fundo claro) e, se for escuro, `fundos.escuro-2` |
| fundo escuro | `fundos.escuro-1` e `cor_caixa` (o mesmo hex com `D9` no fim, 85%) |
| fundo claro | `fundos.claro-1` |
| terceira cor das referências (linhas, ícones, checks) | `cor_apoio`; sem ela, o principal mais claro |
| cor do texto | `cor_texto` no escuro (quase sempre `#FFFFFF`) e `cor_texto_claro` no claro (quase preto) |
| fonte do texto | `fonte` |
| fonte de destaque (itálico, serifa, manuscrita) | `fonte_destaque` |
| fonte de rótulos, pílulas e selo | `fonte_rotulo` |
| legenda com caixa ou solta | `legenda_caixa` e `caixa`: `true` ou `false` |
| maiúsculas | `maiusculas` |
| cantos | `raio` (retos 8, arredondados 24, bem redondos 40) e o `raio` dos cartões da receita |
| fundo predominante | `fundos.padrao` da receita: `escuro-1` ou `claro-1` |
| ritmo | `legenda.palavras_por_bloco` da receita: calmo 3, dinâmico 2 |

Os fundos ficam em `"fundos"` do `estilo-padrao.json`, por papel: `escuro-1`, `escuro-2`, `escuro-3`, `claro-1`, `claro-2`, `claro-3`. Quando as referências mostram mais de um fundo de cada lado, use os delas. Sem isso, derive do mesmo tom: `escuro-2` um pouco mais claro que o `escuro-1` (ou o principal, se for escuro), `escuro-3` mais fundo, quase preto; `claro-2` e `claro-3` um pouco mais escuros e quentes que o `claro-1`. Calcule os hex com Python (mistura de cores). O fundo `alerta` continua o padrão, a não ser que a pessoa peça outro.

**Confirme antes de salvar.** Mostre uma tabela com cada papel, o hex e de onde ele veio (resposta, nome da imagem ou derivado), mais as fontes (avisando qual é aproximação) e a composição. Espere a confirmação e ajuste o que ela pedir.

**Salve**, na pasta desta skill:
1. `estilo-padrao.json`: cores, `fundos`, fontes, `caixa`, `legenda_caixa`, `maiusculas`, `raio` e `"_configurado": true`. Mantenha o `_sobre` e as chaves que não mudaram.
2. `estilos/minha-identidade.json` (a receita, só com as seções da tabela acima) e `estilos/minha-identidade.md` (a descrição, no formato das outras receitas):
   ```json
   {
     "_sobre": "Receita da identidade visual da pessoa, criada na etapa 0. Descrição em minha-identidade.md.",
     "fundos": {"padrao": "claro-1", "brilho": 0.12, "arco": false},
     "cartoes": {
       "escuro": {"cor": "#<escuro-2>E6", "borda": "#<apoio>66", "raio": 28},
       "claro": {"cor": "#FFFFFFE0", "borda": "#FFFFFFFF", "raio": 32}
     },
     "prints": {"borda": 0, "cor_borda": "#<apoio>", "raio": 28, "inclinacao": 0},
     "manchete": {"modelo": "solta"},
     "legenda": {"palavras_por_bloco": 2}
   }
   ```
3. `identidade.md`: o que as imagens mostraram e o que evitar, que o passo 4 lê em todo vídeo:
   ```markdown
   # Identidade visual

   ## Referências analisadas
   - feed-01.png: fundo areia, títulos em negrito grande e soltos, cantos bem redondos.

   ## Composição
   - Legenda: solta, sem caixa, em minúsculas.
   - Fundo predominante: claro. Escuro só em virada ou problema.
   - Ritmo: calmo. Blocos de 3 palavras, formato trocando a cada 3 a 5 s.
   - Texto: extra negrito nos títulos, espaçamento arejado, contraste forte, texto no terço de baixo.
   - Fontes: DM Sans no texto (aproximação da fonte vista no feed).

   ## Evitar
   - Vermelho fora do fundo de alerta.
   ```

Diga em uma linha o que ficou salvo. Se a pessoa trouxe um vídeo, siga para o passo 1; se ela só pediu para configurar, pare aqui.

### 1. Entender o pedido
Pergunte só o que faltar, uma pergunta por vez:
- Quais vídeos e em que ordem.
- Palavra-chave da chamada final (ex: AGENTE).
- Imagens, sons ou transições pedidos, e em que momento da fala.
- Se o vídeo é de uma série (nome, parte e total), para o selo.
- Velocidade. Padrão 1.0; 1.1 deixa a fala mais dinâmica.

O texto na tela é a **legenda da fala** (modo `transcricao`, o padrão). O modo `resumo` só entra se a pessoa pedir "resume a fala".

### 2. Transcrever
`reel transcrever VIDEO1 [VIDEO2 ...] [--pasta nome-do-projeto]`

Com um vídeo, cria `<nome-do-video>-reel/` ao lado dele. Com vários, passe todos na ordem da edição; use `--pasta` para dar um nome à pasta de trabalho. Leia `transcricao.txt`. Nome próprio, termo técnico ou palavra sem sentido: pergunte antes de seguir. Não adivinhe.

### 3. Cortar (com aprovação)
`reel segmentar PASTA`

Gera o `plano.json` com a fala dividida em trechos numerados. O comando também lista **sugestões de corte** (vício solto, tomada repetida): use como ponto de partida, não como decisão. Proponha o que sai, uma linha por item:
- tomada repetida (fica a melhor, normalmente a última);
- frase que começou errada e foi refeita;
- vício solto num trecho sozinho ("então", "né", "tipo");
- final que abre assunto e não fecha.

Se a frase mais forte está no meio, proponha abrir por ela: preencha `"ordem": [ids]` no plano.

**Espere a aprovação.** Só então marque `"manter": false` nos trechos que saem.

### 4. Direção visual e mapa visual (obrigatório)
1. Leia `direcao-visual.md` e, se existir, `identidade.md` (os dois nesta skill). A direção visual decide formato, peças, ritmo, cores e sons; a `identidade.md` diz o que a pessoa prefere e o que evitar, e vale mais quando as duas discordarem.
2. Escolha a receita pelo assunto (`reel receitas` lista as que existem) e preencha `"receita"` no plano. Com `estilos/minha-identidade.json`, ela é a base, e outra receita entra só por seção, quando o assunto pedir: `{"base": "minha-identidade", "prints": "print-anotado"}`.
3. Para cada trecho mantido, preencha `"formato"` (A, B ou C) e, em B e C, `"fundo"` quando fugir do padrão da receita. Monte manchete, peças e sons.
4. Rode `reel mapa PASTA` e mostre a tabela à pessoa, com a receita e os avisos de ritmo.
5. Liste junto as imagens que faltam (seção "Imagens" abaixo).
6. **Espere a aprovação.** Ajuste linha por linha quando a pessoa pedir.

### 5. Montar o plano
Tudo que entra no vídeo fica preso a um trecho (`"trecho": id`), então continua no lugar certo mesmo se os cortes mudarem.
- **`"palavra": "painel"`**: o item entra no instante em que essa palavra (ou expressão) é dita dentro do trecho. Prefira sempre a palavra.
- `atraso`: segundos a mais depois da palavra. `ate_trecho`: estende até outro trecho. `ate_palavra`: a peça sai quando essa palavra é dita (dentro do trecho ou até o `ate_trecho`). `duracao`: corta antes.
- `validar` avisa quando uma palavra não foi encontrada.

**Trechos** (em `"trechos"`):
- `"formato"`: `A` tela cheia (padrão), `B` tela dividida, `C` só gráficos.
- `"fundo"` (B e C): um papel da identidade gravada na etapa 0 (`escuro-1` a `escuro-3`, `claro-1` a `claro-3`), `verde-profundo`, `verde-medio`, `verde-noite`, `off-white`, `areia`, `bege`, `alerta` ou `#RRGGBB`.
- `"painel"` (B): altura do painel da pessoa, de 0.30 a 0.50 (padrão 0.40; com print `grande` no trecho, 0.33).
- `"zoom"` (A): 1.0 a 1.3. Sem o campo, alterna 1.0 e 1.12. Use 1.2 na frase mais forte (até 2 por vídeo).
- `"inclinacao"` (A): graus, -4 a 4. Só numa virada, no máximo 1 por vídeo.
- `"transicao"`: `corte` (padrão), `fade`, `flash`, `zoom`. Só na troca de assunto principal, no máximo 2 por vídeo.

**Receita** (`"receita"`): `"escuro-tecnico"`, `"claro-vidro"`, `"print-anotado"` ou outra criada. Para combinar, por seção: `{"base": "escuro-tecnico", "prints": "print-anotado"}` (seções: fundos, cartoes, prints, manchete, legenda).

**Selo de série** (`"selo"`), só quando a pessoa disser que é série: `{"serie": "Claude na prática", "parte": 3, "total": 7}`.

**Legenda da fala** (`"legenda"`):
- `"palavras_por_bloco"`: 2 (padrão), 1 a 3.
- `"destaques"`: palavras-chave em Playfair Display Italic na cor de destaque. Você escolhe: termo central, resultado e palavra da chamada, 1 a 2 por frase no máximo. Aceita expressões ("Claude Code").
- `"alertas"`: palavras de risco ou erro, em vermelho.
- `"caixa_em"`: a palavra do ponto principal do vídeo, com caixa colorida atrás. No máximo 2.
- `"nomes"`: nomes compostos que nunca se separam entre blocos.
- `"palavra_ativa": false`: mostra o bloco inteiro aceso, sem acender palavra a palavra.
- `"correcoes": {"claude code": "Claude Code", "ia": "IA"}` corrige o que a transcrição escreveu errado (palavras e expressões).
- Números e ordinais ficam destacados sozinhos. Posição, tamanho e caixa mudam sozinhos com o formato.
- A legenda some quando a chamada final entra.

**Textos** (`"textos"`):
```json
{"texto": "o *Claude* certo pra cada tarefa", "tipo": "manchete", "trecho": 1, "ate_trecho": 4}
{"texto": "comenta AGENTE que eu te mando", "tipo": "chamada"}
```
- `manchete`: resumo da seção, até 6 palavras, uma palavra em `*destaque*`. Aparece só nos trechos B e C que cobre. Com `"palavras": ["três", "trabalhos", "para", "automatizar"]` (uma palavra falada para cada palavra da manchete, na ordem) ela entra palavra por palavra, no instante em que cada uma é dita.
- `chamada`: final, em três linhas (COMENTA, a palavra em MAIÚSCULAS grande em Playfair, o complemento). `duracao` padrão 2.5 s.
- `capa`, `bloco`, `lista`: só no modo resumo ou se a pessoa pedir.

**Imagens** (`"imagens"`):
```json
{"arquivo": "/caminho/imagens/painel.png", "trecho": 3, "palavra": "painel", "pilula": "o botão que resolve",
 "anotacoes": [{"tipo": "circulo", "area": [0.70, 0.62, 0.23, 0.10], "palavra": "botão"}], "som_anotacoes": true}
```
- Em B e C o print entra na área das peças; em A, no centro.
- `entrada`: `sobe` (padrão), `pop`, `fade`, `saida` (sem entrada, sai suave), `nenhuma` ou `cresce`. Com `cresce`, a imagem entra pequena e cresce até o tamanho final: `cresce_ate` é a palavra em que ela chega ao tamanho cheio, `pulso_em` dá um pulso com anel numa palavra e `giro` gira de leve (graus). Bom para logo na abertura.
- `grande`: print que precisa de mais altura. `inclinacao`: graus (sem o campo, vale a receita). `pilula`: texto curto abaixo, até 6 palavras. `credito`: obrigatório em imagem de terceiros.
- `anotacoes`: `circulo` (botão, menu), `caixa` (erro, campo importante), `marca` (marca-texto em trecho de texto), `sublinhado` (citação), `seta`. `area` é `[x, y, largura, altura]` em frações da imagem (0 a 1). Abra a imagem e meça. Cada marcação se desenha quando a `palavra` é dita, na ordem da fala.

**Cartões** (`"cartoes"`), na identidade do fundo do trecho:
```json
{"tipo": "numero", "valor": "10h", "rotulo": "economizadas por semana", "trecho": 3, "palavra": "10"}
{"tipo": "lista", "titulo": "O que o agente faz", "itens": ["1º atende", "2º agenda"], "palavras": ["atende", "agenda"], "trecho": 5}
{"tipo": "lista", "check": true, "titulo": "Antes de rodar", "itens": ["Entrada confiável", "Regra clara"], "trecho": 6}
{"tipo": "fluxo", "titulo": "Do pedido à entrega", "itens": ["Gatilho", "Planilha", "IA", "E-mail"], "palavras": [...], "trecho": 7}
{"tipo": "comparacao", "esquerda": {"titulo": "Antes", "itens": ["manual"]}, "direita": {"titulo": "Agora", "itens": ["automático"]}, "palavras": ["antes", "agora"], "trecho": 8}
{"tipo": "palavra", "texto": "sozinho", "trecho": 9, "palavra": "sozinho"}
{"tipo": "icones", "itens": ["linha-do-tempo", "tesoura", "claquete", "play"], "trecho": 2, "palavra": "edição"}
{"tipo": "icones", "itens": ["conversa"], "trecho": 10, "palavra": "mensagem", "acima_da_palavra": true}
{"tipo": "icones", "itens": ["sino"], "trecho": 5, "palavra": "sonoro", "lado": "direita", "destaque_em": "agora"}
{"tipo": "grafico", "icones": ["nota", "moeda"], "palavras": ["financeiro"], "trecho": 8, "palavra": "controle", "ate_palavra": "planilha"}
{"tipo": "conexao", "de": "/caminho/imagens/logo.png", "para": "automacao", "palavras": ["ia", "construir"], "trecho": 19}
{"tipo": "robo", "cena": "celular", "palavras": ["ia", "respondendo", "tudo", "sozinho"], "trecho": 22}
{"tipo": "lista", "robo": true, "icones": ["duvida", "agenda", "relogio", "sacola"], "itens": ["1º tira dúvida", "2º agenda", "3º lembrete", "4º fecha venda"], "palavras": [...], "trecho": 20}
```
- `numero` conta até o valor. `lista` (até 4) e `fluxo` (2 a 5 etapas) acendem item por item; `"som_itens": true` toca um click em cada.
- `palavra`: palavra solta grande em Playfair, entra do desfoque para o nítido. Use em C, até 1 a cada 15 s.
- **Peças animadas** (desenho vetorial quadro a quadro, no mesmo estilo dos cartões): toda peça entra com pop, tem uma pequena interação enquanto está na tela e sai suave.
  - `icones`: de 1 a 4 ícones em placas, em fila no centro da área das peças; cada um entra na sua palavra (`palavras`) ou em sequência rápida. Biblioteca: `linha-do-tempo`, `tesoura`, `claquete`, `play`, `sino`, `moeda`, `nota`, `grafico`, `conversa`, `automacao`, `duvida`, `agenda`, `relogio`, `sacola`. Um item também pode ser o caminho de uma imagem da pessoa (logo, PNG com fundo transparente).
  - `acima_da_palavra`: `true` (a palavra da âncora) ou outra palavra: o ícone fica sem placa, logo acima dessa palavra na legenda. Serve em qualquer formato, inclusive tela cheia.
  - `lado`: `"direita"` ou `"esquerda"` (um ícone só): fica ao lado de uma lista do mesmo trecho, no espaço livre do cartão.
  - `destaque_em`: palavra em que os ícones pulsam com um anel (o `sino` balança forte com ondas). `destaque_atraso` desloca em segundos, para casar com um som.
  - `grafico`: gráfico de barras que cresce com seta para cima, sem números (conceito de crescimento, nunca dado inventado); `icones` põe até 2 ícones flutuando nos cantos, cada um na sua palavra. Só em B e C.
  - `conexao`: `de` e `para` (nome de ícone ou imagem) ligados por uma seta que se desenha na segunda palavra. Mostra uma ferramenta construindo com outra. Só em B e C.
  - `robo` com `"cena": "celular"`: cartão de cantos arredondados (20%) com um robô segurando o celular; a mensagem chega, aparece "digitando" e as respostas entram nas `palavras` (chega, resposta 1, resposta 2, lido). Só em B e C.
  - Na `lista`: `"robo": true` põe um robô que vai até cada item e toca nele quando o item acende. `"icones": [...]` (um por item) mostra o ícone de cada item na fila abaixo da legenda, no formato C.
- Nunca invente dado que não foi dito.

**Sons** (`"sons"`): `{"arquivo": "pop", "trecho": 3, "palavra": "10", "volume": 0.5}`. `arquivo` aceita os sons da skill pelo nome (`pop`, `click`, `ding`, `impacto`, `whoosh`) ou um arquivo da pessoa (só sons livres ou dela). No máximo 1 som a cada 3 s, volume de 0.35 a 0.6.

#### Imagens: ordem obrigatória
1. **Procure** nas pastas do projeto (`imagens/`, `prints/`, `ilustracoes/`) e nos anexos da conversa.
2. **Encontrou:** adapte ao vídeo (formato, área, anotações, pílula) e confirme em uma linha qual arquivo vai em qual trecho.
3. **Não encontrou:** peça à pessoa, dizendo o que a imagem precisa mostrar e em qual trecho entra.
4. **A pessoa não tem:**
   - número, lista, etapas, comparação ou conceito: use os cartões (`numero`, `lista`, `fluxo`, `comparacao`, `palavra`);
   - ilustração realista ou 3D, objeto, cena: entregue o prompt em inglês para o Gemini (modelo em `direcao-visual.md`, seção 10) e siga quando ela mandar a imagem;
   - logo de marca, produto, tela real ou pessoa: nunca gere, peça a imagem real.

#### Modo resumo (só quando pedido)
`"modo_texto": "resumo"` e os blocos em `"textos"` (`capa`, `bloco`, `lista`):
- **Máximo de 6 palavras por bloco.** O comando `validar` recusa mais que isso.
- **Resuma a fala, nunca transcreva.**
- **Destaque números, resultados e a palavra-chave da chamada.** Outros destaques: `*palavra*`.
- **Em listas, numere: 1º, 2º, 3º.** Afirmação curta no lugar de pergunta. Resultado concreto no lugar de benefício vago.
- Um texto a cada 1 ou 2 trechos. **Capa:** proponha 3 opções e deixe a pessoa escolher.

### Estilo
Ordem de prioridade, da mais forte para a mais fraca:
1. O que a pessoa pedir no texto ("destaque em vermelho").
2. A pasta `estilo/` do projeto, ou uma pasta de referência que ela indicar.
3. A receita do plano.
4. O `estilo-padrao.json` desta skill (a identidade da pessoa, gravada na etapa 0).

O que a `identidade.md` manda evitar vale em todos os vídeos, a não ser que a pessoa peça o contrário no próprio pedido.

Com uma pasta de estilo: rode `reel estilo PASTA_ESTILO --aplicar PASTA`, abra as imagens e ajuste o `"estilo"` do plano (cores, fonte, caixa). Diga em uma linha o estilo que vai usar antes de renderizar.

Chaves de `"estilo"`: `cor_texto`, `cor_destaque` (fundo escuro e vídeo), `cor_texto_claro`, `cor_destaque_claro` (fundo claro), `cor_alerta`, `cor_apoio`, `cor_caixa`, `caixa` (caixa atrás dos textos do modo resumo), `legenda_caixa` (caixa na `cor_caixa` atrás de cada linha da legenda da fala; as cores do texto passam a seguir a caixa), `raio`, `fonte`, `fonte_destaque`, `fonte_rotulo`, `tamanho`, `maiusculas` (legenda da fala e textos do resumo em maiúsculas; em C a legenda já é sempre em maiúsculas), `fundos` (nomes extras: `{"azul-noite": "#0B1F33"}`), `ajuste_pecas` (px a mais ou a menos nos textos da tela de cima, manchete e cartões, sem mexer na legenda), `cor_robo` (cor de detalhe do robô e do ponto que corre nas conexões). O que ficar vazio vem do `estilo-padrao.json`. Dourado nunca sobre fundo claro.

### 6. Validar
`reel validar PASTA`

Mostra a duração final, a linha do tempo e os avisos de ritmo. Corrija o que ele apontar.

### 7. Renderizar
`reel renderizar PASTA`

Gera `reel-final.mp4` na pasta: 1080x1920, 30 fps, volume em -14 LUFS (`"volume_padrao": false` desliga). Vídeo horizontal é recortado pelo centro. HDR do iPhone vira cor normal.

### 8. Conferir
`reel quadros PASTA`

Tira um quadro no meio de cada peça e de cada trecho B e C e salva em `PASTA/quadros/`. Abra e confira a lista da seção 15 de `direcao-visual.md`. Ajuste e renderize de novo.

### 9. Entregar
- Caminho do vídeo e duração.
- **Legenda do post**, salva em `PASTA/legenda.txt`: primeira linha com a ideia central, corpo curto (3 a 5 linhas) no tom da pessoa, chamada com a palavra-chave no fim. Hashtags só se ela pedir, até 5.

## Nova referência de estilo (receita)
Quando a pessoa mandar um vídeo de referência e pedir "cria uma receita dessa referência":
1. `reel referencia VIDEO [--a-cada 1.0]` gera folhas de quadros ao lado do vídeo (`<nome>-referencia/`). Para Reels públicos sem o arquivo, peça que a pessoa baixe ou grave a tela.
2. Abra as folhas e analise: formatos e proporção de cada um, legenda (tamanho, posição, caixa, destaque), fundos, peças, movimento, ritmo e chamada.
3. Traduza para a paleta da pessoa e escreva `estilos/<nome>.json` (só as seções fundos, cartoes, prints, manchete, legenda, como nas receitas que já existem) e `estilos/<nome>.md` (descrição no formato das outras). Sem nome, marca ou @ de terceiros.
4. Mostre a receita e espere a aprovação. O vídeo e as folhas nunca entram na skill.

## Ajustes depois da entrega
- "corta a frase X": `"manter": false` no trecho, renderize.
- "abre pela frase X" ou "inverte os vídeos": ajuste `"ordem"`.
- "essa parte em tela dividida" ou "só gráfico aqui": troque o `"formato"` do trecho.
- "fundo claro aqui": `"fundo": "off-white"` (ou areia, bege) no trecho.
- "troca a receita": `"receita"`.
- "legenda mais rápida": `"palavras_por_bloco": 1`. "Mais calma": 3.
- "destaca a palavra X": inclua em `"destaques"`.
- "troca o texto", "tira esse print", "tira o som": edite a lista certa, valide e renderize.
- "sem zoom": `"zoom": {"ativo": false}`. "acelera": `"velocidade": 1.1`.
- "muda a cor": `"estilo": {"cor_destaque": "#HEX"}`.
- "textos de cima maiores": `"estilo": {"ajuste_pecas": 2}` (a legenda da fala não muda).
- "ícone animado nessa palavra": cartão `icones` ancorado na palavra (em tela cheia, `acima_da_palavra`).
- "um robô marcando a lista": `"robo": true` na lista.
- "sem cena vazia": em B e C, toda área de peças sem peça ganha um cartão `icones` ligado à palavra de ênfase.
- "muda meu estilo" ou "configura minha identidade visual": etapa 0.
- "salva esse estilo como padrão": leve o `"estilo"` do plano para o `estilo-padrao.json` da skill (só quando a pessoa pedir).
- "legenda com caixa": `"estilo": {"legenda_caixa": true}`. "Tudo em maiúsculas": `"maiusculas": true`.
- Rosto cortado: `"zoom": {"altura_rosto": 0.3}` (0 é o topo, 1 é a base; vale também para o painel do formato B).

## Regras gerais
- Nunca invente fala, número ou nome na tela. Na dúvida, pergunte.
- Nunca corte sem aprovação. Nunca renderize sem o mapa visual aprovado.
- Nunca apague nem altere os arquivos originais.
- Não coloque música no arquivo. A pessoa escolhe no próprio app, onde já vem licenciada.
