#!/usr/bin/env bash
# Instala a skill editar-reel no Claude Code (Mac e Linux).
set -e

ORIGEM="$(cd "$(dirname "$0")" && pwd)/editar-reel"
DESTINO="$HOME/.claude/skills/editar-reel"

echo "Instalando editar-reel em $DESTINO"

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "Falta o ffmpeg."
  if [ "$(uname)" = "Darwin" ]; then echo "  Instale com: brew install ffmpeg"; else echo "  Instale com: sudo apt install ffmpeg"; fi
  exit 1
fi

PY=""
for c in python3.12 python3.11 python3.10 python3; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; assert sys.version_info >= (3,9)' 2>/dev/null; then PY="$c"; break; fi
done
if [ -z "$PY" ]; then
  echo "Falta Python 3.9 ou mais novo."
  exit 1
fi

mkdir -p "$DESTINO"
# Atualiza os arquivos e mantém a .venv, a sua identidade visual (estilo-padrao.json, identidade.md e a
# receita minha-identidade) e as receitas e fontes que você acrescentou.
IDENTIDADE="estilo-padrao.json identidade.md estilos/minha-identidade.json estilos/minha-identidade.md"
mantive() {
  case "$1" in
    estilo-padrao.json) echo "Mantive o seu estilo-padrao.json." ;;
    identidade.md) echo "Mantive as suas notas de identidade (identidade.md)." ;;
    estilos/*) echo "Mantive a sua receita $(basename "$1")." ;;
    fontes/*) echo "Mantive a sua fonte $(basename "$1")." ;;
  esac
}
GUARDA="$(mktemp -d)"
for arq in $IDENTIDADE; do
  if [ -f "$DESTINO/$arq" ]; then mkdir -p "$GUARDA/$(dirname "$arq")"; cp "$DESTINO/$arq" "$GUARDA/$arq"; fi
done
for pasta in estilos fontes; do
  if [ -d "$DESTINO/$pasta" ]; then mkdir -p "$GUARDA/extras/$pasta"; cp -R "$DESTINO/$pasta/." "$GUARDA/extras/$pasta/"; fi
done
find "$DESTINO" -mindepth 1 -maxdepth 1 ! -name ".venv" -exec rm -rf {} +
cp -R "$ORIGEM/." "$DESTINO/"
# A identidade volta sempre como estava, mesmo que a versão nova traga um arquivo com o mesmo nome.
for arq in $IDENTIDADE; do
  if [ -f "$GUARDA/$arq" ]; then mkdir -p "$DESTINO/$(dirname "$arq")"; cp "$GUARDA/$arq" "$DESTINO/$arq"; mantive "$arq"; fi
done
# Receitas e fontes que você acrescentou; as que vêm com a skill ficam na versão nova.
for pasta in estilos fontes; do
  [ -d "$GUARDA/extras/$pasta" ] || continue
  for arq in "$GUARDA/extras/$pasta"/*; do
    [ -e "$arq" ] || continue
    if [ ! -e "$DESTINO/$pasta/$(basename "$arq")" ]; then
      mkdir -p "$DESTINO/$pasta"; cp -R "$arq" "$DESTINO/$pasta/"; mantive "$pasta/$(basename "$arq")"
    fi
  done
done
rm -rf "$GUARDA"

if [ ! -x "$DESTINO/.venv/bin/python" ]; then
  "$PY" -m venv "$DESTINO/.venv"
fi
"$DESTINO/.venv/bin/python" -m pip install --quiet --upgrade pip
"$DESTINO/.venv/bin/python" -m pip install --quiet -r "$DESTINO/requirements.txt"

"$DESTINO/.venv/bin/python" "$DESTINO/motor/cli.py" checar || true
echo
echo "Pronto. No Claude Code, chame /editar-reel"
if grep -Eq '"_configurado"[[:space:]]*:[[:space:]]*false' "$DESTINO/estilo-padrao.json" 2>/dev/null; then
  echo "No primeiro /editar-reel, o Claude pergunta a sua identidade visual (cores, fontes, imagens do seu feed"
  echo "e o jeito do texto) antes de editar. Depois ele usa o seu visual em todos os reels."
else
  echo "Para trocar a sua identidade visual, diga no Claude Code: configura minha identidade visual"
fi
