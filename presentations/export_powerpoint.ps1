# Optionaler PDF- und Vorschau-Export mit lokal installiertem Microsoft PowerPoint.
# Aus dem Repository-Hauptverzeichnis starten; Datenpipeline bleibt unverändert.
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$pptxPath = Join-Path $PSScriptRoot 'teil1_verkehrsunfaelle_zuerich.pptx'
$pdfPath = Join-Path $PSScriptRoot 'teil1_verkehrsunfaelle_zuerich.pdf'
$previewPath = Join-Path $projectRoot '.venv/folienvorschau'
New-Item -ItemType Directory -Force -Path $previewPath | Out-Null
$powerPoint = $null
$deck = $null
try {
    $powerPoint = New-Object -ComObject PowerPoint.Application
    # ReadOnly, Untitled und WithWindow: Datei ohne sichtbares Bearbeitungsfenster öffnen.
    $deck = $powerPoint.Presentations.Open($pptxPath, -1, 0, 0)
    $deck.SaveAs($pdfPath, 32)
    $deck.Export($previewPath, 'PNG', 1600, 900)
    Write-Output ('Exportiert: {0} Folien, PDF und PNG-Vorschau' -f $deck.Slides.Count)
} finally {
    if ($null -ne $deck) { $deck.Close() }
    if ($null -ne $powerPoint -and $powerPoint.Presentations.Count -eq 0) {
        $powerPoint.Quit()
    }
}
