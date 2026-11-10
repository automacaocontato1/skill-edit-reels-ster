"""Desenho vetorial com Pillow: formas, caminhos e curvas com translação, giro e escala exatos.

Desenha numa tela maior (supersampling) e reduz no fim, para bordas lisas. Serve aos ícones
animados (icones.py) sem depender de bibliotecas de SVG.

Coordenadas: as do sprite final. Cores: "#RRGGBB", "#RRGGBBAA" ou tupla RGBA.
"""
import math
import re

from PIL import Image, ImageDraw, ImageFilter


def rgba(cor, opacidade=1.0):
    if cor is None:
        return None
    if isinstance(cor, tuple):
        r, g, b = cor[:3]
        a = cor[3] if len(cor) > 3 else 255
    else:
        h = cor.lstrip("#")
        if len(h) == 6:
            h += "FF"
        r, g, b, a = (int(h[i:i + 2], 16) for i in (0, 2, 4, 6))
    return (r, g, b, max(0, min(255, int(round(a * opacidade)))))


def _mult(m, n):
    a, b, c, d, e, f = m
    a2, b2, c2, d2, e2, f2 = n
    return (a * a2 + b * d2, a * b2 + b * e2, a * c2 + b * f2 + c,
            d * a2 + e * d2, d * b2 + e * e2, d * c2 + e * f2 + f)


class Tela:
    def __init__(self, largura, altura, ss=3):
        self.w, self.h, self.ss = largura, altura, ss
        self.img = Image.new("RGBA", (largura * ss, altura * ss), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img, "RGBA")
        self.m = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0)
        self.op = 1.0
        self._pilha = []

    # transformações
    def salvar(self):
        self._pilha.append((self.m, self.op))

    def restaurar(self):
        self.m, self.op = self._pilha.pop()

    def mover(self, dx, dy):
        self.m = _mult(self.m, (1, 0, dx, 0, 1, dy))

    def girar(self, graus, cx=0.0, cy=0.0):
        if not graus:
            return
        r = math.radians(graus)
        c, s = math.cos(r), math.sin(r)
        self.mover(cx, cy)
        self.m = _mult(self.m, (c, -s, 0, s, c, 0))
        self.mover(-cx, -cy)

    def escalar(self, sx, sy=None, cx=0.0, cy=0.0):
        sy = sx if sy is None else sy
        self.mover(cx, cy)
        self.m = _mult(self.m, (sx, 0, 0, 0, sy, 0))
        self.mover(-cx, -cy)

    def opacidade(self, fator):
        self.op *= max(0.0, min(1.0, fator))

    # pontos e larguras
    def _p(self, x, y):
        a, b, c, d, e, f = self.m
        return ((a * x + b * y + c) * self.ss, (d * x + e * y + f) * self.ss)

    def _w(self, w):
        a, b, c, d, e, f = self.m
        return w * math.sqrt(abs(a * e - b * d)) * self.ss

    def _cor(self, cor, extra=1.0):
        return rgba(cor, self.op * extra)

    # primitivas
    def poligono(self, pontos, preenche=None, traco=None, largura=0, opacidade=1.0, fechado=True):
        pts = [self._p(x, y) for x, y in pontos]
        if len(pts) < 2:
            return
        if preenche and fechado and len(pts) >= 3:
            self.d.polygon(pts, fill=self._cor(preenche, opacidade))
        if traco and largura:
            w = max(1, int(round(self._w(largura))))
            cor = self._cor(traco, opacidade)
            seq = pts + [pts[0]] if fechado else pts
            self.d.line(seq, fill=cor, width=w, joint="curve")
            if not fechado:
                for x, y in (pts[0], pts[-1]):
                    self.d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=cor)

    def linha(self, pontos, cor, largura, opacidade=1.0):
        self.poligono(pontos, traco=cor, largura=largura, opacidade=opacidade, fechado=False)

    def elipse(self, cx, cy, rx, ry, preenche=None, traco=None, largura=0, opacidade=1.0):
        n = max(24, int(max(rx, ry) * self._w(1) / 2))
        n = min(n, 160)
        pts = [(cx + rx * math.cos(2 * math.pi * k / n), cy + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]
        self.poligono(pts, preenche, traco, largura, opacidade)

    def circulo(self, cx, cy, r, preenche=None, traco=None, largura=0, opacidade=1.0):
        self.elipse(cx, cy, r, r, preenche, traco, largura, opacidade)

    def arco(self, cx, cy, r, ini, fim, cor, largura, opacidade=1.0):
        """Arco de ini a fim (graus, 0 à direita, sentido horário)."""
        n = max(6, int(abs(fim - ini) / 5))
        pts = [(cx + r * math.cos(math.radians(ini + (fim - ini) * k / n)),
                cy + r * math.sin(math.radians(ini + (fim - ini) * k / n))) for k in range(n + 1)]
        self.linha(pts, cor, largura, opacidade)

    def retangulo(self, x, y, w, h, raio=0, preenche=None, traco=None, largura=0, opacidade=1.0):
        raio = max(0, min(raio, w / 2, h / 2))
        if raio <= 0:
            pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
        else:
            pts = []
            for cx, cy, a0 in ((x + w - raio, y + raio, -90), (x + w - raio, y + h - raio, 0),
                               (x + raio, y + h - raio, 90), (x + raio, y + raio, 180)):
                for k in range(9):
                    a = math.radians(a0 + 90 * k / 8)
                    pts.append((cx + raio * math.cos(a), cy + raio * math.sin(a)))
        self.poligono(pts, preenche, traco, largura, opacidade)

    def caminho(self, d, preenche=None, traco=None, largura=0, opacidade=1.0):
        """Caminho com comandos absolutos M L Q C Z (como no SVG)."""
        for pontos, fechado in _caminho_em_pontos(d):
            if preenche and fechado:
                self.poligono(pontos, preenche=preenche, opacidade=opacidade)
            if traco and largura:
                self.poligono(pontos, traco=traco, largura=largura, opacidade=opacidade, fechado=fechado)

    def imagem(self, img, cx, cy, tam, giro=0.0, opacidade=1.0):
        """Cola uma imagem (logo, ícone em PNG) centrada em cx, cy com o maior lado = tam."""
        a, b, c, d, e, f = self.m
        escala = math.sqrt(abs(a * e - b * d))
        angulo = math.degrees(math.atan2(d, a)) + giro
        lado = max(2, int(tam * escala * self.ss))
        im = img.copy()
        im.thumbnail((lado, lado), Image.LANCZOS)
        if im.width < lado and im.height < lado:
            r = lado / max(im.size)
            im = im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)
        if angulo:
            im = im.rotate(-angulo, resample=Image.BICUBIC, expand=True)
        op = self.op * opacidade
        if op < 1:
            im.putalpha(im.getchannel("A").point(lambda v: int(v * op)))
        px, py = self._p(cx, cy)
        self.img.alpha_composite(im, (int(px - im.width / 2), int(py - im.height / 2)))

    def resultado(self, sombra=0.0):
        """Imagem final no tamanho do sprite. sombra: opacidade da sombra suave (0 sem sombra)."""
        im = self.img.resize((self.w, self.h), Image.LANCZOS)
        if sombra:
            a = im.getchannel("A").filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * sombra))
            s = Image.new("RGBA", im.size, (0, 0, 0, 255))
            s.putalpha(a)
            base = Image.new("RGBA", im.size, (0, 0, 0, 0))
            base.alpha_composite(s, (0, 10))
            base.alpha_composite(im)
            im = base
        return im


_TOKENS = re.compile(r"[MLQCZmlqcz]|-?\d*\.?\d+(?:e-?\d+)?")


def _bezier(p0, p1, p2, p3=None, n=16):
    pts = []
    for k in range(1, n + 1):
        t = k / n
        if p3 is None:
            x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
            y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        else:
            x = (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t ** 2 * p2[0] + t ** 3 * p3[0]
            y = (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t ** 2 * p2[1] + t ** 3 * p3[1]
        pts.append((x, y))
    return pts


def _caminho_em_pontos(d):
    toks = _TOKENS.findall(d)
    sub, atual, cmd, i = [], [], None, 0
    while i < len(toks):
        tk = toks[i]
        if tk.isalpha():
            cmd = tk.upper()
            i += 1
            if cmd == "Z":
                if atual:
                    sub.append((atual, True))
                atual = []
            continue
        nums = []
        quantos = {"M": 2, "L": 2, "Q": 4, "C": 6}[cmd]
        for _ in range(quantos):
            nums.append(float(toks[i]))
            i += 1
        if cmd == "M":
            if atual:
                sub.append((atual, False))
            atual = [(nums[0], nums[1])]
            cmd = "L"
        elif cmd == "L":
            atual.append((nums[0], nums[1]))
        elif cmd == "Q":
            atual += _bezier(atual[-1], (nums[0], nums[1]), (nums[2], nums[3]))
        elif cmd == "C":
            atual += _bezier(atual[-1], (nums[0], nums[1]), (nums[2], nums[3]), (nums[4], nums[5]))
    if atual:
        sub.append((atual, False))
    return sub
