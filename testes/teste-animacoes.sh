#!/usr/bin/env bash
# Teste das peças animadas, sem baixar o modelo de transcrição.
# Gera uma "pessoa" sintética, um logo, uma transcrição falsa e um plano com manchete palavra por palavra,
# imagem que cresce com pulso, ícones animados (em fila, ao lado da lista e acima da palavra), sino com
# destaque, lista com robô, lista com ícones por item, gráfico crescente, conexão, robô com celular e
# ajuste_pecas. Roda mapa, validar, renderizar e quadros.
# Uso: bash testes/teste-animacoes.sh [pasta-de-saida]
set -e

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
M="$RAIZ/editar-reel/motor/cli.py"
PY="${PYTHON:-python3}"
T="${1:-$(mktemp -d)}"
mkdir -p "$T/imagens" "$T/reel"
cd "$T"

"$PY" - <<'EOF'
from PIL import Image, ImageDraw
im = Image.new("RGB", (1080, 1920), "#C9B8A6"); d = ImageDraw.Draw(im)
d.rectangle([0, 1250, 1080, 1920], fill="#B5A08A")
d.ellipse([390, 470, 690, 830], fill="#E2B497")
d.rounded_rectangle([210, 860, 870, 1920], radius=220, fill="#2B4C7E")
d.ellipse([470, 610, 500, 640], fill="#333"); d.ellipse([580, 610, 610, 640], fill="#333")
im.save("pessoa.png")
lg = Image.new("RGBA", (400, 400), (0, 0, 0, 0)); d = ImageDraw.Draw(lg)
d.ellipse([20, 20, 380, 380], fill="#E8742A"); d.ellipse([140, 140, 260, 260], fill="#FFFFFF")
lg.save("imagens/logo.png")
EOF
ffmpeg -y -loglevel error -loop 1 -framerate 30 -i pessoa.png -f lavfi -i "sine=f=330:d=34" -t 34 \
  -c:v libx264 -preset veryfast -pix_fmt yuv420p -c:a aac -shortest parte1.mp4
ffmpeg -y -loglevel error -loop 1 -framerate 30 -i pessoa.png -f lavfi -i "sine=f=440:d=4" -t 4 \
  -c:v libx264 -preset veryfast -pix_fmt yuv420p -c:a aac -shortest parte2.mp4

"$PY" - "$T" <<'EOF'
import json, sys
T = sys.argv[1]
def frase(texto, ini, fim):
    ws = texto.split(); passo = (fim - ini) / len(ws)
    return [{"p": w, "i": round(ini + k * passo, 2), "f": round(ini + (k + 0.85) * passo, 2)} for k, w in enumerate(ws)]
v1, t = [], 0.2
for texto, dur in [("Três dicas para automatizar o trabalho.", 3.2), ("Primeiro edição de vídeo com cortes.", 2.8),
                   ("A lista tem legenda e efeito sonoro agora.", 4.0), ("O controle financeiro cresce todo mês.", 3.6),
                   ("Tudo dentro do seu WhatsApp mesmo.", 2.6), ("A IA constrói junto com a ferramenta.", 3.4),
                   ("Tira dúvidas agenda e fecha a venda.", 4.2), ("A IA responde tudo sozinha.", 3.0)]:
    v1 += frase(texto, t, t + dur)
    t += dur + 0.4
v2 = frase("Comenta AGENTE que eu te mando.", 0.3, 2.6)
json.dump({"videos": [{"arquivo": f"{T}/parte1.mp4", "duracao": 34.0, "palavras": v1},
                      {"arquivo": f"{T}/parte2.mp4", "duracao": 4.0, "palavras": v2}]},
          open("reel/transcricao.json", "w"), ensure_ascii=False)
EOF

"$PY" "$M" segmentar reel > /dev/null
"$PY" - "$T" <<'EOF'
import json, sys
T = sys.argv[1]
logo = f"{T}/imagens/logo.png"
p = json.load(open("reel/plano.json"))
visual = {1: ("B", "verde-profundo"), 2: ("B", "off-white"), 3: ("B", "off-white"), 4: ("B", "verde-profundo"),
          5: ("A", None), 6: ("B", "areia"), 7: ("C", "areia"), 8: ("C", "areia"), 9: ("A", None)}
for tr in p["trechos"]:
    tr["formato"], fundo = visual[tr["id"]]
    if fundo:
        tr["fundo"] = fundo
    if tr["formato"] == "B":
        tr["painel"] = 0.45
p["receita"] = "claro-vidro"
p["estilo"] = {"ajuste_pecas": 2}
p["correcoes"] = {"ia": "IA", "whatsapp": "WhatsApp"}
p["legenda"] = {"destaques": ["automatizar", "WhatsApp"]}
p["textos"] = [{"texto": "3 dicas para *automatizar*", "tipo": "manchete", "trecho": 1,
                "palavras": ["três", "dicas", "para", "automatizar"]},
               {"texto": "1º edição de *vídeo*", "tipo": "manchete", "trecho": 2, "ate_trecho": 3},
               {"texto": "comenta AGENTE que eu te mando", "tipo": "chamada", "duracao": 2.2}]
p["imagens"] = [{"arquivo": logo, "trecho": 1, "palavra": "automatizar", "entrada": "cresce", "cresce_ate": "trabalho",
                 "pulso_em": "trabalho", "largura": 280, "inclinacao": 0, "giro": 15}]
p["cartoes"] = [
    {"tipo": "icones", "itens": ["linha-do-tempo", "tesoura", "claquete", "play"], "trecho": 2, "palavra": "edição"},
    {"tipo": "lista", "check": True, "robo": True, "titulo": "Feito com IA", "itens": ["Legenda", "Efeito sonoro"],
     "palavras": ["legenda", "efeito"], "trecho": 3},
    {"tipo": "icones", "itens": ["sino"], "trecho": 3, "palavra": "sonoro", "lado": "direita", "destaque_em": "agora"},
    {"tipo": "grafico", "icones": ["nota", "moeda"], "palavras": ["financeiro", "mês"], "trecho": 4, "palavra": "controle"},
    {"tipo": "icones", "itens": ["conversa"], "trecho": 5, "palavra": "whatsapp", "acima_da_palavra": True},
    {"tipo": "conexao", "de": logo, "para": "automacao", "palavras": ["ia", "junto"], "trecho": 6, "palavra": "ia"},
    {"tipo": "lista", "robo": True, "icones": ["duvida", "agenda", "sacola"], "titulo": "A IA faz",
     "itens": ["1º Tira dúvida", "2º Agenda", "3º Fecha venda"], "palavras": ["tira", "agenda", "fecha"], "trecho": 7},
    {"tipo": "robo", "cena": "celular", "palavras": ["ia", "responde", "tudo", "sozinha"], "trecho": 8},
]
p["sons"] = [{"arquivo": "ding", "trecho": 3, "palavra": "agora", "volume": 0.45},
             {"arquivo": "whoosh", "trecho": 4, "volume": 0.4}]
json.dump(p, open("reel/plano.json", "w"), ensure_ascii=False, indent=2)
EOF

"$PY" "$M" mapa reel
"$PY" "$M" validar reel
"$PY" "$M" renderizar reel
"$PY" "$M" quadros reel > /dev/null
echo
echo "Teste ok. Vídeo: $T/reel/reel-final.mp4"
echo "Quadros para conferir: $T/reel/quadros/"
