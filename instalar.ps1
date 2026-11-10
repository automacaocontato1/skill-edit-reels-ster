# Instala a skill editar-reel no Claude Code (Windows).
$ErrorActionPreference = 'Stop'

$Origem = Join-Path $PSScriptRoot 'editar-reel'
$Destino = Join-Path $HOME '.claude\skills\editar-reel'

Write-Host "Instalando editar-reel em $Destino"

if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Host 'Falta o ffmpeg. Instale com: winget install Gyan.FFmpeg (depois feche e abra o terminal)'
    exit 1
}

$Py = $null
foreach ($c in @('py', 'python')) {
    if (Get-Command $c -ErrorAction SilentlyContinue) {
        & $c -c 'import sys; assert sys.version_info >= (3,9)' 2>$null
        if ($LASTEXITCODE -eq 0) { $Py = $c; break }
    }
}
if (-not $Py) {
    Write-Host 'Falta Python 3.9 ou mais novo. Instale com: winget install Python.Python.3.12'
    exit 1
}

New-Item -ItemType Directory -Force -Path $Destino | Out-Null
# Atualiza os arquivos e mantém a .venv, a sua identidade visual (estilo-padrao.json, identidade.md e a
# receita minha-identidade) e as receitas e fontes que você acrescentou. Tudo é copiado como está
# (sem regravar o texto), para o arquivo não ganhar BOM.
$Identidade = @('estilo-padrao.json', 'identidade.md', 'estilos\minha-identidade.json', 'estilos\minha-identidade.md')
function Mantive($Arq) {
    $Nome = Split-Path -Leaf $Arq
    if ($Arq -eq 'estilo-padrao.json') { Write-Host 'Mantive o seu estilo-padrao.json.' }
    elseif ($Arq -eq 'identidade.md') { Write-Host 'Mantive as suas notas de identidade (identidade.md).' }
    elseif ($Arq -like 'estilos\*') { Write-Host "Mantive a sua receita $Nome." }
    elseif ($Arq -like 'fontes\*') { Write-Host "Mantive a sua fonte $Nome." }
}
$Guarda = Join-Path ([System.IO.Path]::GetTempPath()) ('editar-reel-' + [guid]::NewGuid())
New-Item -ItemType Directory -Force -Path (Join-Path $Guarda 'extras') | Out-Null
foreach ($Arq in $Identidade) {
    $Atual = Join-Path $Destino $Arq
    if (Test-Path $Atual) {
        $Copia = Join-Path $Guarda $Arq
        New-Item -ItemType Directory -Force -Path (Split-Path $Copia) | Out-Null
        Copy-Item -Force $Atual $Copia
    }
}
foreach ($Pasta in @('estilos', 'fontes')) {
    $Atual = Join-Path $Destino $Pasta
    if (Test-Path $Atual) { Copy-Item -Recurse -Force $Atual (Join-Path $Guarda "extras\$Pasta") }
}
Get-ChildItem -Force $Destino | Where-Object { $_.Name -ne '.venv' } | Remove-Item -Recurse -Force
Copy-Item -Recurse -Force (Join-Path $Origem '*') $Destino
# A identidade volta sempre como estava, mesmo que a versão nova traga um arquivo com o mesmo nome.
foreach ($Arq in $Identidade) {
    $Copia = Join-Path $Guarda $Arq
    if (Test-Path $Copia) {
        $Alvo = Join-Path $Destino $Arq
        New-Item -ItemType Directory -Force -Path (Split-Path $Alvo) | Out-Null
        Copy-Item -Force $Copia $Alvo
        Mantive $Arq
    }
}
# Receitas e fontes que você acrescentou; as que vêm com a skill ficam na versão nova.
foreach ($Pasta in @('estilos', 'fontes')) {
    $Salvos = Join-Path $Guarda "extras\$Pasta"
    if (-not (Test-Path $Salvos)) { continue }
    $PastaAlvo = Join-Path $Destino $Pasta
    New-Item -ItemType Directory -Force -Path $PastaAlvo | Out-Null
    Get-ChildItem -Force $Salvos | ForEach-Object {
        $Alvo = Join-Path $PastaAlvo $_.Name
        if (-not (Test-Path $Alvo)) { Copy-Item -Recurse -Force $_.FullName $Alvo; Mantive "$Pasta\$($_.Name)" }
    }
}
Remove-Item -Recurse -Force $Guarda

$VenvPy = Join-Path $Destino '.venv\Scripts\python.exe'
if (-not (Test-Path $VenvPy)) { & $Py -m venv (Join-Path $Destino '.venv') }
& $VenvPy -m pip install --quiet --upgrade pip
& $VenvPy -m pip install --quiet -r (Join-Path $Destino 'requirements.txt')

& $VenvPy (Join-Path $Destino 'motor\cli.py') checar
Write-Host ''
Write-Host 'Pronto. No Claude Code, chame /editar-reel'
$Configurado = $true
try { $Configurado = (Get-Content -Raw (Join-Path $Destino 'estilo-padrao.json') | ConvertFrom-Json)._configurado -ne $false } catch {}
if (-not $Configurado) {
    Write-Host 'No primeiro /editar-reel, o Claude pergunta a sua identidade visual (cores, fontes, imagens do seu feed'
    Write-Host 'e o jeito do texto) antes de editar. Depois ele usa o seu visual em todos os reels.'
} else {
    Write-Host 'Para trocar a sua identidade visual, diga no Claude Code: configura minha identidade visual'
}
