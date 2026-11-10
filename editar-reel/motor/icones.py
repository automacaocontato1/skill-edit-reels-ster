"""Ícones animados e peças animadas: desenho vetorial (vetor.py), quadro a quadro.

Estilo único: traço arredondado na cor de destaque do fundo claro (ou branco no escuro), detalhe na
cor de apoio (dourado só no escuro), dentro de placas iguais às dos cartões da receita. Toda peça entra
com pop, tem uma pequena interação enquanto está na tela e sai suave.

Cada função sprite_* grava uma sequência de PNG (só a região da peça) e devolve
{"padrao", "x", "y", "quadros"} para o render sobrepor na posição certa.
"""
import math
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path

from PIL import Image

from cartelas import _visual_cartao
from vetor import Tela
from visual import ALTURA, LARGURA, y_legenda

FPS = 30
ACENTO_PADRAO = "#EB6E55"


# ---------- curvas ----------
def c01(x):
    return max(0.0, min(1.0, x))


def volta(x, s=1.9):
    x = c01(x) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def suave(x):
    x = c01(x)
    return x * x * (3 - 2 * x)


def desacelera(x):
    return 1 - (1 - c01(x)) ** 3


def entra(t, t0, d=0.32):
    """(escala, opacidade) da entrada com pop."""
    x = (t - t0) / d
    if x <= 0:
        return 0.0, 0.0
    return volta(x), c01(x / 0.35)


def sai(t, t1, d=0.2):
    """(fator de escala, opacidade) da saída suave que termina em t1."""
    x = c01((t1 - t) / d)
    return 0.86 + 0.14 * x, x


@contextmanager
def grupo(tv, cx, cy, esc=1.0, op=1.0, giro=0.0, dx=0.0, dy=0.0):
    tv.salvar()
    tv.mover(dx, dy)
    tv.girar(giro, cx, cy)
    tv.escalar(esc, None, cx, cy)
    tv.opacidade(op)
    try:
        yield
    finally:
        tv.restaurar()


# ---------- cores ----------
def _mistura(hexa, outro, f):
    a = [int(hexa.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(outro.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{int(x + (y - x) * f):02X}" for x, y in zip(a, b))


def cores_icone(tema, estilo, receita=None):
    vis = _visual_cartao(tema, estilo, receita)
    acento = estilo.get("cor_robo") or ACENTO_PADRAO
    if tema == "claro":
        return {"placa": vis["cor"], "borda": vis["borda"], "traco": estilo["cor_destaque_claro"],
                "det": estilo["cor_apoio"], "det2": estilo["cor_apoio"], "contra": "#FFFFFF",
                "suave": _mistura(estilo["cor_apoio"], "#FFFFFF", 0.86), "acento": acento, "sombra": 0.28,
                "barras": (estilo["cor_apoio"], estilo["cor_destaque_claro"])}
    return {"placa": vis["cor"], "borda": vis["borda"] or "#289A8B66", "traco": "#FFFFFF",
            "det": estilo["cor_destaque"], "det2": _mistura(estilo["cor_apoio"], "#FFFFFF", 0.3), "contra": "#03332C",
            "suave": (255, 255, 255, 36), "acento": acento, "sombra": 0.45,
            "barras": (_mistura(estilo["cor_apoio"], "#FFFFFF", 0.3), estilo["cor_destaque"])}


def placa(tv, cx, cy, tam, k, raio=0.28):
    tv.retangulo(cx - tam / 2, cy - tam / 2, tam, tam, tam * raio, preenche=k["placa"],
                 traco=k["borda"], largura=3 if k["borda"] else 0)


# ---------- ícones (caixa 100 x 100) ----------
def _check(tv, pts, p, cor, largura=7):
    if p <= 0:
        return
    total = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
    resta, seq = total * p, [pts[0]]
    for a, b in zip(pts, pts[1:]):
        seg = math.dist(a, b)
        if resta <= 0:
            break
        f = min(1, resta / seg)
        seq.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
        resta -= seg
    tv.linha(seq, cor, largura)


def ic_linha_do_tempo(tv, t, k, info):
    tv.retangulo(10, 22, 80, 56, 10, preenche=k["suave"], traco=k["traco"], largura=7)
    tv.retangulo(20, 33, 38, 8, 4, preenche=k["det"])
    tv.retangulo(30, 47, 48, 8, 4, preenche=k["traco"], opacidade=0.75)
    tv.retangulo(20, 61, 28, 8, 4, preenche=k["det"], opacidade=0.8)
    x = 24 + 52 * ((t * 0.7) % 1)
    tv.linha([(x, 27), (x, 73)], k["traco"], 4)
    tv.poligono([(x - 6, 24), (x + 6, 24), (x, 31)], preenche=k["traco"])


def ic_tesoura(tv, t, k, info):
    a = 9 * abs(math.sin(math.pi * 1.8 * t))
    for sinal, y_alca, y0, y1 in ((1, 34, 40, 64), (-1, 70, 64, 40)):
        tv.salvar()
        tv.girar(sinal * a, 54, 52)
        tv.circulo(24, y_alca, 11, preenche=k["suave"], traco=k["traco"], largura=7)
        tv.linha([(33, y0), (86, y1)], k["traco"], 7)
        tv.restaurar()
    tv.circulo(54, 52, 4, preenche=k["det"])


def ic_claquete(tv, t, k, info):
    ciclo = (t * 1.2) % 1
    if ciclo < 0.2:
        ang = -26 + 26 * suave(ciclo / 0.2)
    elif ciclo > 0.55:
        ang = -26 * suave((ciclo - 0.55) / 0.45)
    else:
        ang = 0
    tv.retangulo(16, 44, 68, 40, 7, preenche=k["suave"], traco=k["traco"], largura=7)
    tv.linha([(26, 60), (74, 60)], k["traco"], 5, opacidade=0.5)
    tv.linha([(26, 72), (58, 72)], k["traco"], 5, opacidade=0.5)
    tv.salvar()
    tv.girar(ang, 16, 42)
    tv.retangulo(16, 28, 68, 14, 4, preenche=k["traco"])
    for x in (30, 46, 62, 78):
        tv.linha([(x, 30), (x - 6, 40)], k["contra"], 4)
    tv.restaurar()


def ic_play(tv, t, k, info):
    f = (t * 1.1) % 1
    tv.circulo(50, 50, 34 + 14 * f, traco=k["det"], largura=4, opacidade=0.6 * (1 - f))
    tv.circulo(50, 50, 34, preenche=k["suave"], traco=k["traco"], largura=7)
    tv.poligono([(43, 35), (67, 50), (43, 65)], preenche=k["det"], traco=k["det"], largura=4)


def ic_sino(tv, t, k, info):
    dest = info.get("destaque")
    if dest is None:
        ang, ondas = 9 * math.sin(2 * math.pi * 1.1 * t), 0.0
    else:
        ang = 24 * math.exp(-dest * 2.2) * math.sin(2 * math.pi * 3.2 * dest)
        ondas = c01(1 - abs(dest - 0.25) / 0.5) if dest < 0.9 else 0.0
    if ondas > 0:
        for i, r in enumerate((10, 20)):
            op = ondas * (0.9 - 0.35 * i)
            tv.caminho(f"M{14 - r * 0.4} {34 - r * 0.3} Q{4 - r * 0.6} 46 {14 - r * 0.4} {58 + r * 0.3}", traco=k["det"], largura=5, opacidade=op)
            tv.caminho(f"M{86 + r * 0.4} {34 - r * 0.3} Q{96 + r * 0.6} 46 {86 + r * 0.4} {58 + r * 0.3}", traco=k["det"], largura=5, opacidade=op)
    tv.salvar()
    tv.girar(ang, 50, 12)
    tv.caminho("M50 16 C33 16 28 32 28 46 L28 62 L19 73 L81 73 L72 62 L72 46 C72 32 67 16 50 16 Z",
               preenche=k["suave"], traco=k["traco"], largura=7)
    tv.circulo(50, 12, 5, preenche=k["traco"])
    tv.circulo(50 + ang * 0.35, 82, 7, preenche=k["det"])
    tv.restaurar()


def ic_moeda(tv, t, k, info):
    sx = abs(math.cos(math.pi * 0.9 * t)) * 0.75 + 0.25
    tv.salvar()
    tv.escalar(sx, 1, 50, 50)
    tv.circulo(50, 50, 31, preenche="#DFAC16", traco="#AB8208", largura=4)
    tv.circulo(50, 50, 22, traco="#AB8208", largura=3)
    tv.caminho("M58 40 C55 35 42 35 42 43 C42 51 58 49 58 57 C58 65 45 65 42 60", traco="#7A5C05", largura=4.5)
    tv.linha([(50, 32), (50, 68)], "#7A5C05", 4.5)
    tv.restaurar()


def ic_nota(tv, t, k, info):
    tv.retangulo(12, 28, 76, 44, 8, preenche=k["det2"] if k["traco"] == "#FFFFFF" else k["det"], traco="#FFFFFF", largura=4)
    tv.retangulo(19, 35, 62, 30, 5, traco="#FFFFFF", largura=2.5, opacidade=0.55)
    tv.circulo(50, 50, 9, traco="#FFFFFF", largura=4)
    tv.circulo(26, 50, 3, preenche="#FFFFFF")
    tv.circulo(74, 50, 3, preenche="#FFFFFF")


def ic_grafico(tv, t, k, info):
    tv.linha([(16, 82), (86, 82)], k["traco"], 6)
    for i, (x, a) in enumerate(((22, 0.35), (42, 0.55), (62, 0.8))):
        h = 50 * a * (0.9 + 0.1 * math.sin(2 * math.pi * (0.8 * t - i * 0.2)))
        tv.retangulo(x, 76 - h, 14, h, 4, preenche=k["det"] if i < 2 else k["traco"])
    p = 1 + 0.12 * math.sin(2 * math.pi * 1.5 * t)
    tv.linha([(18, 52), (44, 36), (58, 42), (82, 18)], k["traco"], 6)
    tv.linha([(82 - 13 * p, 18), (82, 18), (82, 18 + 13 * p)], k["traco"], 6)


def ic_conversa(tv, t, k, info):
    tv.caminho("M50 12 C29 12 13 27 13 47 C13 55 16 62 20 68 L15 87 L35 81 C40 83 45 84 50 84 "
               "C71 84 87 68 87 47 C87 27 71 12 50 12 Z", preenche="#25D366", traco="#FFFFFF", largura=4)
    for i, x in enumerate((35, 50, 65)):
        y = 47 - 5 * max(0.0, math.sin(2 * math.pi * (t * 1.6 - i * 0.18)))
        tv.circulo(x, y, 5.5, preenche="#FFFFFF")


def ic_automacao(tv, t, k, info):
    tv.linha([(30, 50), (42, 50)], k["traco"], 5)
    tv.caminho("M62 50 C70 50 70 32 76 32", traco=k["traco"], largura=5)
    tv.caminho("M62 50 C70 50 70 68 76 68", traco=k["traco"], largura=5)
    tv.circulo(20, 50, 10, preenche=k["suave"], traco=k["traco"], largura=5)
    tv.retangulo(41, 39, 22, 22, 6, preenche=k["det"], traco=k["traco"], largura=5)
    tv.circulo(84, 32, 8.5, preenche=k["suave"], traco=k["traco"], largura=5)
    tv.circulo(84, 68, 8.5, preenche=k["suave"], traco=k["traco"], largura=5)
    f = (t * 1.4) % 1
    if f < 0.35:
        x, y = 30 + 12 * f / 0.35, 50
    else:
        g = (f - 0.35) / 0.65
        x, y = 62 + 14 * g, 50 - 18 * suave(g)
    tv.circulo(x, y, 4, preenche=k["acento"])


def ic_duvida(tv, t, k, info):
    g = 7 * math.sin(2 * math.pi * 1.2 * t)
    tv.caminho("M24 18 L76 18 Q88 18 88 30 L88 58 Q88 70 76 70 L46 70 L30 84 L32 70 L24 70 Q12 70 12 58 L12 30 Q12 18 24 18 Z",
               preenche=k["suave"], traco=k["traco"], largura=7)
    tv.salvar()
    tv.girar(g, 50, 46)
    tv.caminho("M41 36 C41 27 59 27 59 36 C59 43 50 43 50 51", traco=k["det"], largura=7)
    tv.circulo(50, 60, 4, preenche=k["det"])
    tv.restaurar()


def ic_agenda(tv, t, k, info):
    tv.retangulo(15, 24, 70, 62, 10, preenche=k["suave"], traco=k["traco"], largura=7)
    tv.linha([(15, 40), (85, 40)], k["traco"], 6)
    tv.linha([(34, 16), (34, 30)], k["traco"], 7)
    tv.linha([(66, 16), (66, 30)], k["traco"], 7)
    _check(tv, [(37, 61), (46, 70), (65, 51)], desacelera((t - 0.25) / 0.4), k["det"])


def ic_relogio(tv, t, k, info):
    g = 8 * math.sin(2 * math.pi * 3.2 * t) * (0.5 + 0.5 * math.sin(2 * math.pi * 0.7 * t))
    m = math.radians(360 * ((t * 0.5) % 1))
    tv.salvar()
    tv.girar(g, 50, 54)
    tv.caminho("M20 30 Q22 19 36 18", traco=k["det"], largura=7)
    tv.caminho("M64 18 Q78 19 80 30", traco=k["det"], largura=7)
    tv.circulo(50, 54, 29, preenche=k["suave"], traco=k["traco"], largura=7)
    tv.linha([(50, 54), (50, 38)], k["traco"], 6)
    tv.linha([(50, 54), (50 + 13 * math.sin(m), 54 - 13 * math.cos(m))], k["det"], 5)
    tv.linha([(30, 80), (25, 87)], k["traco"], 6)
    tv.linha([(70, 80), (75, 87)], k["traco"], 6)
    tv.restaurar()


def ic_sacola(tv, t, k, info):
    tv.poligono([(22, 36), (78, 36), (74, 86), (26, 86)], preenche=k["suave"], traco=k["traco"], largura=7)
    tv.caminho("M37 36 C37 18 63 18 63 36", traco=k["traco"], largura=7)
    _check(tv, [(38, 61), (47, 70), (64, 53)], desacelera((t - 0.25) / 0.4), k["det"])


ICONES = {
    "linha-do-tempo": ic_linha_do_tempo, "tesoura": ic_tesoura, "claquete": ic_claquete, "play": ic_play,
    "sino": ic_sino, "moeda": ic_moeda, "nota": ic_nota, "grafico": ic_grafico, "conversa": ic_conversa,
    "automacao": ic_automacao, "duvida": ic_duvida, "agenda": ic_agenda, "relogio": ic_relogio, "sacola": ic_sacola,
}


@lru_cache(maxsize=16)
def _imagem(caminho):
    return Image.open(Path(caminho).expanduser()).convert("RGBA")


def item_valido(item):
    return item in ICONES or Path(str(item)).expanduser().is_file()


def desenhar_icone(tv, item, cx, cy, tam, t, k, info=None):
    """Ícone da biblioteca pelo nome, ou imagem da pessoa (logo, PNG) pelo caminho."""
    tv.salvar()
    tv.mover(cx - tam / 2, cy - tam / 2)
    tv.escalar(tam / 100)
    if item in ICONES:
        ICONES[item](tv, t, k, info or {})
    else:
        tv.imagem(_imagem(str(item)), 50, 50, 80, giro=8 * math.sin(2 * math.pi * 0.25 * t))
    tv.restaurar()


# ---------- robô (caixa 200 x 240, virado para a esquerda) ----------
def desenhar_robo(tv, t, k, braco=0.0, feliz=False, segura=False):
    """braco: 0 recolhido, 1 esticado tocando. Flutua de leve, pisca e mexe a antena."""
    verde = k["robo_traco"]
    b = 4 * math.sin(2 * math.pi * 0.9 * t)
    pisca = 0.12 if (t % 2.6) < 0.1 else 1.0
    tv.elipse(100, 234, 46 - b, 7, preenche=(0, 0, 0, 30))
    tv.salvar()
    tv.mover(0, b)
    tv.salvar()
    tv.girar(6 * math.sin(2 * math.pi * 1.3 * t), 100, 40)
    tv.linha([(100, 40), (100, 16)], verde, 6)
    tv.circulo(100, 13, 9, preenche=k["acento"])
    tv.restaurar()
    tv.retangulo(40, 38, 120, 92, 30, preenche="#FFFFFF", traco=verde, largura=6)
    tv.retangulo(56, 56, 88, 54, 20, preenche="#03332C")
    for x in (82, 118):
        tv.elipse(x, 81, 9, 11 * pisca, preenche="#5FE3CB")
    tv.caminho("M86 97 Q100 109 114 97" if feliz else "M88 99 Q100 105 112 99", traco="#5FE3CB", largura=4)
    tv.retangulo(88, 128, 24, 10, 3, preenche=verde)
    tv.retangulo(54, 136, 92, 76, 26, preenche="#FFFFFF", traco=verde, largura=6)
    tv.circulo(100, 172, 15, preenche=k["acento"])
    for a, b2, c, d in ((100, 162, 100, 182), (90, 172, 110, 172), (93, 165, 107, 179), (107, 165, 93, 179)):
        tv.linha([(a, b2), (c, d)], "#FFFFFF", 3)
    tv.caminho("M146 158 Q166 170 160 194", traco=verde, largura=10)
    tv.circulo(160, 197, 8, preenche="#FFFFFF", traco=verde, largura=5)
    if not segura:
        alcance = 30 + 62 * braco
        mx, my = 52 - alcance, 150 - 8 * braco
        tv.caminho(f"M54 156 Q{(54 + mx) / 2} {my + 2} {mx} {my}", traco=verde, largura=10)
        tv.circulo(mx, my, 8, preenche="#FFFFFF", traco=verde, largura=5)
        tv.linha([(mx, my), (mx - 12, my - 2)], verde, 7)
    tv.restaurar()


def _cores_robo(tema, estilo, receita):
    k = cores_icone(tema, estilo, receita)
    k["robo_traco"] = estilo["cor_destaque_claro"]
    return k


# ---------- gravação ----------
def _gravar(pasta, prefixo, n, caixa, desenhar, sombra, ss=None):
    x0, y0, w, h = (int(round(v)) for v in caixa)
    x0, y0 = max(0, x0), max(0, y0)
    w, h = min(w, LARGURA - x0), min(h, ALTURA - y0)
    ss = ss or (3 if w * h < 260_000 else 2)
    for i in range(n):
        tv = Tela(w, h, ss)
        tv.mover(-x0, -y0)
        desenhar(tv, i / FPS)
        tv.resultado(sombra).save(pasta / f"{prefixo}-{i:04d}.png", compress_level=1)
    return {"padrao": str(pasta / f"{prefixo}-%04d.png"), "x": x0, "y": y0, "quadros": n}


def _quadros(c):
    return max(1, int(round((c["fim_final"] - c["inicio_final"]) * FPS)))


def _centro_area(c, padrao_a):
    area = c.get("_area")
    return (area[0] + area[1]) / 2 if area else padrao_a


# ---------- peças ----------
def sprite_icones(c, estilo, receita, pasta, prefixo):
    """Cartão 'icones': até 4 ícones em placas, cada um entra na sua palavra."""
    k = cores_icone(c.get("_tema", "video"), estilo, receita)
    itens = c["itens"]
    n = len(itens)
    tempos = c.get("itens_tempo") or [c["inicio_final"] + 0.1 + 0.15 * i for i in range(n)]
    dest = c.get("destaque_tempo")
    ini, fim = c["inicio_final"], c["fim_final"]
    com_placa = not c.get("_acima")
    tam = 150 if c.get("_acima") else {1: 210, 2: 190}.get(n, 170)
    if c.get("_acima"):
        xw, yl = c["_acima"]
        centros = [(xw, yl - tam / 2 - 16)]
    else:
        cy = _centro_area(c, y_legenda("A") - 210)
        if c.get("lado") in ("esquerda", "direita") and n == 1:
            centros = [(400 if c["lado"] == "esquerda" else 680, cy)]
        else:
            passo = tam + 45
            centros = [(LARGURA / 2 + (i - (n - 1) / 2) * passo, cy) for i in range(n)]
    meio = 0.85 * tam + 20
    xs = [x for x, _ in centros]
    caixa = (min(xs) - meio, centros[0][1] - meio, max(xs) - min(xs) + 2 * meio, 2 * meio)

    def desenhar(tv, tl):
        t = ini + tl
        es, eo = sai(t, fim)
        for item, (cx, cy), ti in zip(itens, centros, tempos):
            esc, op = entra(t, ti)
            if op <= 0:
                continue
            info, pulso = {}, 1.0
            if dest is not None and t >= dest:
                f = (t - dest) / 0.45
                if item == "sino":
                    info["destaque"] = t - dest
                elif f <= 1:
                    pulso = 1 + 0.14 * math.sin(math.pi * f)
                    tv.circulo(cx, cy, tam * (0.5 + 0.35 * f), traco=k["det"], largura=5, opacidade=(1 - f) * eo)
            dy = -6 * math.sin(2 * math.pi * 0.8 * (t - ti))
            with grupo(tv, cx, cy, esc * es * pulso, op * eo, dy=dy):
                if com_placa:
                    placa(tv, cx, cy, tam, k)
                desenhar_icone(tv, item, cx, cy, tam * (0.68 if com_placa else 1.0), t - ti, k, info)
    return _gravar(pasta, prefixo, _quadros(c), caixa, desenhar, k["sombra"])


def sprite_icones_lista(c, estilo, receita, pasta, prefixo):
    """Ícone de cada item de uma lista, em fila abaixo da legenda (formato C)."""
    k = cores_icone(c.get("_tema", "claro"), estilo, receita)
    itens = c["icones"]
    tempos = c.get("itens_tempo") or [c["inicio_final"] + 0.35 + 0.6 * i for i in range(len(itens))]
    ini, fim = c["inicio_final"], c["fim_final"]
    tam, passo = 160, 210
    cy = y_legenda("C") + 180
    centros = [(LARGURA / 2 + (i - (len(itens) - 1) / 2) * passo, cy) for i in range(len(itens))]
    meio = 0.85 * tam + 20
    caixa = (centros[0][0] - meio, cy - meio, centros[-1][0] - centros[0][0] + 2 * meio, 2 * meio)

    def desenhar(tv, tl):
        t = ini + tl
        es, eo = sai(t, fim)
        for item, (cx, cy_), ti in zip(itens, centros, tempos):
            esc, op = entra(t, ti)
            if op <= 0:
                continue
            dy = -5 * math.sin(2 * math.pi * 0.8 * (t - ti))
            with grupo(tv, cx, cy_, esc * es, op * eo, dy=dy):
                placa(tv, cx, cy_, tam, k)
                desenhar_icone(tv, item, cx, cy_, tam * 0.7, t - ti, k)
    return _gravar(pasta, prefixo, _quadros(c), caixa, desenhar, k["sombra"])


def sprite_robo_lista(c, estilo, receita, pasta, prefixo):
    """Robô que vai até cada item da lista e toca nele quando o item acende."""
    k = _cores_robo(c.get("_tema", "claro"), estilo, receita)
    x0, y0, larg, alt, pad = c["_caixa"]
    ys = [y0 + pad + yt + asc * 0.62 for yt, asc, _ in c["_itens_y"]]
    tempos = c.get("itens_tempo") or []
    ini, fim = c["inicio_final"], c["fim_final"]
    es_r = 0.8
    rx = x0 + larg - 100
    caixa = (x0 + larg - 470, y0 - 40, 510, alt + 80)
    t_ent = ini + 0.15

    def alvo(t):
        y = ys[0]
        for i, ti in enumerate(tempos):
            if i > 0 and t >= ti - 0.35:
                y = ys[i - 1] + (ys[i] - ys[i - 1]) * suave((t - ti + 0.35) / 0.3)
        return y

    def desenhar(tv, tl):
        t = ini + tl
        esc, op = entra(t, t_ent, 0.35)
        es, eo = sai(t, fim)
        braco = max([math.exp(-((t - ti) / 0.16) ** 2) for ti in tempos] or [0])
        cy = alvo(t)
        x = rx - 45 * braco
        for ti in tempos:
            f = (t - ti) / 0.35
            if 0 <= f <= 1:
                fx, fy = x - 152 * es_r - 8, cy - 18 * es_r
                for j in range(6):
                    a = j * math.pi / 3
                    r1, r2 = 10 + 26 * f, 16 + 34 * f
                    tv.linha([(fx + r1 * math.cos(a), fy + r1 * math.sin(a)), (fx + r2 * math.cos(a), fy + r2 * math.sin(a))],
                             k["det"], 4, opacidade=(1 - f) * eo)
        with grupo(tv, x, cy, esc * es, op * eo):
            tv.salvar()
            tv.mover(x - 100 * es_r, cy - 160 * es_r)
            tv.escalar(es_r)
            desenhar_robo(tv, t, k, braco, feliz=bool(tempos) and t > tempos[-1])
            tv.restaurar()
    return _gravar(pasta, prefixo, _quadros(c), caixa, desenhar, k["sombra"])


def sprite_grafico(c, estilo, receita, pasta, prefixo):
    """Gráfico de barras que cresce com seta de tendência, e até 2 ícones flutuando nos cantos."""
    tema = c.get("_tema", "escuro")
    k = cores_icone(tema, estilo, receita)
    ini, fim = c["inicio_final"], c["fim_final"]
    cx, cy = LARGURA / 2, _centro_area(c, 760)
    wk, hk = 560, 360
    icones = (c.get("icones") or [])[:2]
    tempos = c.get("itens_tempo") or [ini + 0.3 + 0.3 * i for i in range(len(icones))]
    cantos = [(cx - 360, cy - 138), (cx + 360, cy + 142)]
    alturas = [0.28, 0.42, 0.38, 0.62, 0.86]
    cor_barra, cor_ultima = k["barras"]
    caixa = (cx - 470, cy - 260, 940, 520)

    def desenhar(tv, tl):
        t = ini + tl
        esc, op = entra(t, ini, 0.35)
        es, eo = sai(t, fim, 0.25)
        x0, y0 = cx - wk / 2, cy - hk / 2
        with grupo(tv, cx, cy, esc * es, op * eo):
            tv.retangulo(x0, y0, wk, hk, 40, preenche=k["placa"], traco=k["borda"], largura=3 if k["borda"] else 0)
            base_y, topo_y = y0 + hk - 60, y0 + 50
            for gy in (0.33, 0.66):
                yy = base_y - (base_y - topo_y) * gy
                tv.linha([(x0 + 50, yy), (x0 + wk - 50, yy)], k["traco"], 2, opacidade=0.15)
            tv.linha([(x0 + 50, base_y), (x0 + wk - 50, base_y)], k["traco"], 4, opacidade=0.5)
            bw, gap = 58, 32
            topos = []
            for i, a in enumerate(alturas):
                bx = x0 + 80 + i * (bw + gap)
                h = (base_y - topo_y) * a * desacelera((t - ini - 0.25 - 0.12 * i) / 0.45)
                if h > 0.5:
                    tv.retangulo(bx, base_y - h, bw, h, min(10, h / 2), preenche=cor_ultima if i == 4 else cor_barra)
                topos.append((bx + bw / 2, base_y - (base_y - topo_y) * a - 26))
            p = desacelera((t - ini - 0.85) / 0.6)
            if p > 0:
                total = sum(math.dist(a, b) for a, b in zip(topos, topos[1:]))
                resta, seq, ang = total * p, [topos[0]], 0.0
                for a, b in zip(topos, topos[1:]):
                    seg = math.dist(a, b)
                    if resta <= 0:
                        break
                    f = min(1, resta / seg)
                    seq.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
                    ang = math.atan2(b[1] - a[1], b[0] - a[0])
                    resta -= seg
                tv.linha(seq, k["traco"], 7)
                ponta = seq[-1]
                pul = 1 + 0.12 * math.sin(2 * math.pi * 1.5 * max(0.0, t - ini - 1.45))
                for lado in (-0.55, 0.55):
                    tv.linha([ponta, (ponta[0] - 26 * pul * math.cos(ang + lado), ponta[1] - 26 * pul * math.sin(ang + lado))],
                             k["traco"], 7)
        for i, (item, (bx, by), ti) in enumerate(zip(icones, cantos, tempos)):
            m, mo = entra(t, ti)
            if mo <= 0:
                continue
            dy = 7 * math.sin(2 * math.pi * 0.7 * (t - i * 0.4))
            with grupo(tv, bx, by, m * es, mo * eo, dy=dy):
                placa(tv, bx, by, 140, k)
                desenhar_icone(tv, item, bx, by, 100, t - ti, k)
    return _gravar(pasta, prefixo, _quadros(c), caixa, desenhar, k["sombra"])


def sprite_conexao(c, estilo, receita, pasta, prefixo):
    """Dois ícones ligados por uma seta que se desenha: um entra, a seta liga, o outro entra."""
    k = cores_icone(c.get("_tema", "claro"), estilo, receita)
    ini, fim = c["inicio_final"], c["fim_final"]
    tempos = c.get("itens_tempo") or [ini + 0.05, ini + 0.6]
    t_de, t_seta = tempos[0], tempos[-1]
    cy = _centro_area(c, 760)
    ca, cb, tam = LARGURA / 2 - 270, LARGURA / 2 + 270, 210
    caixa = (ca - 200, cy - 200, cb - ca + 400, 400)

    def desenhar(tv, tl):
        t = ini + tl
        es, eo = sai(t, fim)
        for item, cx, ti in ((c["de"], ca, t_de), (c["para"], cb, t_seta + 0.3)):
            esc, op = entra(t, ti, 0.35)
            if op > 0:
                with grupo(tv, cx, cy, esc * es, op * eo):
                    placa(tv, cx, cy, tam, k)
                    desenhar_icone(tv, item, cx, cy, tam * 0.7, t - ti, k)
        p = desacelera((t - t_seta + 0.05) / 0.4)
        if p > 0:
            xa, xb = ca + 125, cb - 125
            xe = xa + (xb - xa) * p
            x = xa
            while x < xe - 14:
                tv.circulo(x, cy, 4.5, preenche=k["traco"], opacidade=eo)
                x += 22
            tv.linha([(xe - 22, cy - 20), (xe, cy), (xe - 22, cy + 20)], k["traco"], 9, opacidade=eo)
            if p >= 1:
                f = ((t - t_seta - 0.35) * 1.3) % 1
                tv.circulo(xa + (xb - xa) * f, cy, 9, preenche=k["acento"], opacidade=eo)
    return _gravar(pasta, prefixo, _quadros(c), caixa, desenhar, k["sombra"])


def sprite_robo_celular(c, estilo, receita, pasta, prefixo):
    """Cartão com cantos de 20%: robô segurando um celular e respondendo a conversa sozinho."""
    k = _cores_robo("claro", estilo, receita)
    ini, fim = c["inicio_final"], c["fim_final"]
    marcos = c.get("itens_tempo") or [ini + 0.4, ini + 0.9, ini + 1.4, ini + 1.8]
    t_msg, t_r1, t_r2, t_ok = (marcos + [marcos[-1]] * 4)[:4]
    tam = 540
    cx, cy = LARGURA / 2, _centro_area(c, 760)
    o_x, o_y = cx - tam / 2, cy - tam / 2
    caixa = (o_x - 30, o_y - 30, tam + 60, tam + 60)
    fundo1, fundo2 = estilo["cor_destaque_claro"], "#03332C"

    def bolha(tv, x, y, w, h, cor, linhas, t0, t):
        esc, op = entra(t, t0, 0.28)
        if op <= 0:
            return
        with grupo(tv, x + w / 2, y + h / 2, esc, op):
            tv.retangulo(x, y, w, h, 14, preenche=cor)
            for i, lw in enumerate(linhas):
                tv.retangulo(x + 14, y + 14 + i * 16, lw, 8, 4, preenche=(91, 107, 102, 140))

    def desenhar(tv, tl):
        t = ini + tl
        esc, op = entra(t, ini + 0.03, 0.38)
        es, eo = sai(t, fim)
        with grupo(tv, cx, cy, esc * es, op * eo):
            tv.retangulo(o_x, o_y, tam, tam, tam * 0.2, preenche=_mistura(fundo1, fundo2, 0.35))
            tv.circulo(o_x + 175, o_y + 175, 130, preenche=(40, 154, 139, 46))
            tv.salvar()
            tv.mover(o_x + 20, o_y + 160)
            tv.escalar(1.25)
            desenhar_robo(tv, t, k, 0, feliz=t > t_ok, segura=True)
            tv.restaurar()
            px, py, pw, ph = o_x + 300, o_y + 95, 190, 360
            tv.salvar()
            tv.girar(-6 + 2 * math.sin(2 * math.pi * 0.6 * (t - ini)), px + pw / 2, py + ph / 2)
            tv.retangulo(px, py, pw, ph, 30, preenche="#101614", traco="#FFFFFFD9", largura=4)
            tv.retangulo(px + 10, py + 12, pw - 20, ph - 24, 22, preenche="#EFE7DE")
            tv.retangulo(px + 10, py + 12, pw - 20, 46, 22, preenche="#03332C")
            tv.retangulo(px + 10, py + 36, pw - 20, 22, 0, preenche="#03332C")
            tv.circulo(px + 36, py + 35, 11, preenche="#DFAC16")
            tv.retangulo(px + 54, py + 29, 70, 10, 5, preenche="#FFFFFFCC")
            bx = px + 18
            bolha(tv, bx, py + 74, 112, 44, "#FFFFFF", [80, 52], t_msg, t)
            if t_msg + 0.25 <= t < t_r1:
                tv.retangulo(bx, py + 124, 72, 32, 14, preenche="#FFFFFF")
                for i in range(3):
                    yy = py + 140 - 4 * max(0.0, math.sin(2 * math.pi * (t * 2 - i * 0.2)))
                    tv.circulo(bx + 22 + i * 16, yy, 5, preenche="#6B7A75")
            bolha(tv, px + pw - 142, py + 132, 124, 60, "#D9FDD3", [92, 84, 50], t_r1, t)
            bolha(tv, px + pw - 142, py + 204, 124, 44, "#D9FDD3", [96, 60], t_r2, t)
            if t >= t_ok:
                f = c01((t - t_ok) / 0.25)
                for yy in (py + 184, py + 240):
                    xx = px + pw - 46
                    tv.linha([(xx, yy), (xx + 5, yy + 5), (xx + 14, yy - 5)], "#34B7F1", 3, opacidade=f)
                    tv.linha([(xx + 8, yy), (xx + 13, yy + 5), (xx + 22, yy - 5)], "#34B7F1", 3, opacidade=f)
            tv.restaurar()
            toque = max(math.exp(-((t - tt) / 0.14) ** 2) for tt in (t_r1, t_r2))
            hx, hy = px + 8 + 14 * toque, py + 268 - 16 * toque
            ombro = (o_x + 20 + 140 * 1.25, o_y + 160 + 160 * 1.25)
            curva = f"M{ombro[0]} {ombro[1]} Q{(ombro[0] + hx) / 2} {hy + 60} {hx} {hy}"
            tv.caminho(curva, traco="#FFFFFF", largura=20)
            tv.caminho(curva, traco=k["robo_traco"], largura=12)
            tv.circulo(hx, hy, 15, preenche="#FFFFFF", traco=k["robo_traco"], largura=6)
    return _gravar(pasta, prefixo, _quadros(c), caixa, desenhar, 0.35)


def sprite_cresce(im, png, pasta, prefixo):
    """Imagem que cresce de pequena até o tamanho final, com pulso opcional numa palavra."""
    base = Image.open(png).convert("RGBA")
    bbox = base.getbbox() or (0, 0, LARGURA, ALTURA)
    peca = base.crop(bbox)
    cx, cy = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2
    ini, fim = im["inicio_final"], im["fim_final"]
    t_cheio = im.get("cresce_tempo") or ini + 0.6
    t_cheio = max(ini + 0.25, min(t_cheio, fim - 0.05))
    t_pulso = im.get("pulso_tempo")
    giro = float(im.get("giro") or 0)
    lado = int(max(peca.size) * 1.45)
    x0, y0 = int(cx - lado / 2), int(cy - lado / 2)
    n = max(1, int(round((fim - ini) * FPS)))
    for i in range(n):
        t = ini + i / FPS
        esc = 0.12 + 0.88 * desacelera((t - ini) / (t_cheio - ini))
        if t_pulso is not None and t >= t_pulso:
            esc *= 1 + 0.1 * math.sin(math.pi * c01((t - t_pulso) / 0.35))
        op = c01((t - ini) / 0.15) * c01((fim - t) / 0.15)
        quadro = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
        w, h = max(1, int(peca.width * esc)), max(1, int(peca.height * esc))
        p = peca.resize((w, h), Image.LANCZOS)
        if giro:
            p = p.rotate(-giro * c01((t - ini) / max(0.3, fim - ini)), resample=Image.BICUBIC, expand=True)
        if op < 1:
            p.putalpha(p.getchannel("A").point(lambda v, op=op: int(v * op)))
        quadro.alpha_composite(p, (lado // 2 - p.width // 2, lado // 2 - p.height // 2))
        if t_pulso is not None and t >= t_pulso and (t - t_pulso) < 0.45:
            f = (t - t_pulso) / 0.45
            tv = Tela(lado, lado, 2)
            r = max(peca.size) * 0.5 * (1 + 0.4 * f)
            tv.circulo(lado / 2, lado / 2, r, traco=im.get("_cor_anel", "#289A8B"), largura=5, opacidade=0.8 * (1 - f) * op)
            quadro.alpha_composite(tv.resultado())
        quadro.save(pasta / f"{prefixo}-{i:04d}.png", compress_level=1)
    return {"padrao": str(pasta / f"{prefixo}-%04d.png"), "x": x0, "y": y0, "quadros": n}


def sprite_revelar(camadas, tempos, ini, fim, caixa, pasta, prefixo):
    """Camadas (uma por palavra, no layout final) que entram uma a uma: desfoque de posição e opacidade."""
    x0, y0, w, h = caixa
    recortes = [cam.crop((x0, y0, x0 + w, y0 + h)) for cam in camadas]
    n = max(1, int(round((fim - ini) * FPS)))
    for i in range(n):
        t = ini + i / FPS
        quadro = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        for cam, ti in zip(recortes, tempos):
            p = c01((t - ti) / 0.2)
            if p <= 0:
                continue
            a = cam if p >= 1 else cam.copy()
            if p < 1:
                a.putalpha(a.getchannel("A").point(lambda v, p=p: int(v * p)))
            quadro.alpha_composite(a, (0, int(round(16 * (1 - p) ** 2))))
        quadro.save(pasta / f"{prefixo}-{i:04d}.png", compress_level=1)
    return {"padrao": str(pasta / f"{prefixo}-%04d.png"), "x": x0, "y": y0, "quadros": n}
