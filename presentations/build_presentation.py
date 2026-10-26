"""Editierbare Teil-1-Folien und Lernleitfaden aus dem eingefrorenen Datenbestand.

Ausführung nach Installation von presentations/requirements.txt:
    python presentations/build_presentation.py
Kein Download und keine Änderung an Raw-/Processed-Daten. Diagramme werden aus
derselben SQLite-Datei wie im Analyse-Notebook gebildet. PowerPoint/PDF-Export
und visuelle Kontrolle erfolgen separat mit Microsoft PowerPoint.
"""

import hashlib
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Lokale optionale Installation bleibt ausserhalb der Pipeline-Umgebung.
LOCAL_PACKAGES = ROOT / ".venv" / "presentation_packages"
if LOCAL_PACKAGES.exists():
    sys.path.insert(0, str(LOCAL_PACKAGES))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt

OUT = ROOT / "presentations"
ASSETS = OUT / "assets"
ASSETS.mkdir(exist_ok=True)
SUMMARY = json.loads((ROOT / "data/processed/analysis_summary.json").read_text(encoding="utf8"))
DB = ROOT / "data/processed/accidents.sqlite"
assert hashlib.sha256(DB.read_bytes()).hexdigest().upper() == SUMMARY["database_sha256"]
with sqlite3.connect(DB.resolve().as_uri() + "?mode=ro", uri=True) as connection:
    DATA = pd.read_sql_query("SELECT * FROM accidents", connection)
assert len(DATA) == SUMMARY["rows"] == 70767

NAVY = "102C3B"
TEAL = "087E83"
ORANGE = "C56A35"
BG = "F4F6F5"
WHITE = "FFFFFF"
GREY = "536773"
PALE = "E3EFED"
LIGHT = "CFD9DD"
FONT = "Aptos"
SOURCE = "Daten: Open Data Zürich / Bundesamt für Strassen ASTRA · Snapshot 13.10.2026"
prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
prs.core_properties.title = "Verkehrsunfälle in Zürich | Data Engineering, Teil 1"
prs.core_properties.author = "Ruben Souto, Issa Fawaz, Drin Muslija"
prs.core_properties.subject = "Reproduzierbare Datenpipeline, Hypothesentests und Forschungsfragen"
NOTES = []


def rgb(value):
    return RGBColor.from_string(value)


def rect(s, x, y, w, h, fill, radius=False, line=None):
    shape = s.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
        Inches(x), Inches(y), Inches(w), Inches(h),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb(fill)
    if line:
        shape.line.color.rgb = rgb(line)
    else:
        shape.line.fill.background()
    if radius:
        shape.adjustments[0] = 0.08
    return shape


def text(s, x, y, w, h, value, size=20, color=NAVY, bold=False, font=FONT):
    box = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.015)
    tf.margin_top = tf.margin_bottom = Inches(0.015)
    for i, line in enumerate(value.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.font.name = font
        p.font.size = Pt(size)
        p.font.bold = bold
        p.font.color.rgb = rgb(color)
        p.space_after = Pt(7)
    return box


def slide(label, title, subtitle="", dark=False):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = rgb(NAVY if dark else BG)
    color = WHITE if dark else NAVY
    rect(s, 0, 0, 13.333, 0.055, TEAL)
    text(s, 0.6, 0.33, 11.8, 0.32, label.upper(), 10.5, "79C9C1" if dark else TEAL, True)
    text(s, 0.6, 0.87, 12.1, 0.68, title, 31, color, True)
    if subtitle:
        text(s, 0.6, 1.63, 12.1, 0.6, subtitle, 17, LIGHT if dark else GREY)
    n = len(prs.slides)
    text(s, 0.6, 7.13, 10.9, 0.2, "ZHAW · Data Engineering HS26 · Souto / Fawaz / Muslija", 9,
         LIGHT if dark else GREY)
    text(s, 12.02, 7.08, 0.7, 0.3, f"{n:02}", 11, LIGHT if dark else TEAL, True)
    return s


def note(s, title, seconds, speech, understand):
    value = f"{title}\nRichtzeit: {seconds} Sekunden\n\n{speech}\n\nVerstehen: {understand}"
    s.notes_slide.notes_text_frame.text = value
    NOTES.append((title, seconds, speech, understand))


def card(s, x, y, w, h, label, body, accent=TEAL, body_size=19):
    rect(s, x, y, w, h, WHITE, True)
    rect(s, x, y, 0.045, h, accent)
    text(s, x + 0.23, y + 0.2, w - 0.43, 0.5, label, 19, accent, True)
    text(s, x + 0.23, y + 0.88, w - 0.43, h - 1.03, body, body_size)


def ribbon(s, value, y=6.35, fill=PALE, size=17):
    rect(s, 0.6, y, 12.1, 0.53, fill, True)
    text(s, 0.81, y + 0.09, 11.65, 0.36, value, size, NAVY, True)


def source(s, value=SOURCE):
    text(s, 0.62, 6.91, 11.6, 0.19, value, 8, GREY)


def picture(s, path, x, y, w, h):
    from PIL import Image

    with Image.open(path) as im:
        iw, ih = im.size
    scale = min(w / iw, h / ih)
    ww, hh = iw * scale, ih * scale
    s.shapes.add_picture(str(path), Inches(x + (w - ww) / 2), Inches(y + (h - hh) / 2),
                         width=Inches(ww), height=Inches(hh))


def chart_style(ax):
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color("#CFD9DD")
    ax.tick_params(colors="#536773", length=0, pad=7)
    ax.set_axisbelow(True)
    ax.grid(axis="y", color="#E3E9E9", linewidth=0.8)
    ax.set_facecolor("#FFFFFF")


plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 13,
                     "text.color": "#102C3B", "axes.labelcolor": "#536773"})
hours = DATA.groupby(["is_weekend", "AccidentHour"]).size().unstack(fill_value=0)
shares = hours.div(hours.sum(axis=1), axis=0) * 100
fig, ax = plt.subplots(figsize=(10.7, 4.5), facecolor="white")
for group, label, color in [(0, "Werktage (Mo–Fr)", TEAL), (1, "Wochenende (Sa–So)", ORANGE)]:
    ax.plot(shares.columns, shares.loc[group], color="#" + color, linewidth=3, label=label)
ax.axvspan(0, 5, color="#E3EFED", alpha=0.65, zorder=0)
ax.set(xlabel="Unfallstunde", ylabel="Anteil innerhalb der Gruppe (%)", xlim=(0, 23), ylim=(0, 9))
ax.set_xticks(range(0, 24, 3))
ax.legend(frameon=False, loc="upper left", ncol=2, fontsize=11)
chart_style(ax)
fig.tight_layout(pad=1.4)
fig.savefig(ASSETS / "vortrag_f1.png", dpi=200)
plt.close(fig)

fig, ax = plt.subplots(figsize=(10.7, 4.5), facecolor="white")
labels = ["Fussgänger", "Velo", "Motorrad"]
xx = np.arange(3)
for involved, shift, color, label in [(0, -0.17, "A7B6BF", "Ohne jeweilige Beteiligung"),
                                      (1, 0.17, TEAL, "Mit jeweiliger Beteiligung")]:
    vals = [next(r["severe_share_pct"] for r in SUMMARY["f2_severe_shares"]
                 if r["participation"] == item and r["involved"] == involved) for item in labels]
    bars = ax.bar(xx + shift, vals, width=0.3, color="#" + color, label=label)
    ax.bar_label(bars, labels=[f"{v:.2f} %".replace(".", ",") for v in vals], padding=6, fontsize=12)
ax.set_xticks(xx, labels)
ax.set(ylabel="Anteil schwerer / tödlicher Unfälle (%)", ylim=(0, 32))
ax.legend(frameon=False, loc="upper right", fontsize=10)
chart_style(ax)
fig.tight_layout(pad=1.4)
fig.savefig(ASSETS / "vortrag_f2.png", dpi=200)
plt.close(fig)

annual = pd.DataFrame(SUMMARY["annual_counts"])
participation = pd.DataFrame(SUMMARY["injury_participation_shares_by_year"])
fig, axes = plt.subplots(1, 2, figsize=(13, 4.5), facecolor="white")
for field, label, color in [("total", "Alle registrierten Unfälle", NAVY),
                             ("person_injury", "Personenschadenunfälle", TEAL)]:
    axes[0].plot(annual["year"], annual[field], color="#" + color, linewidth=2.6, label=label)
axes[0].axvline(2015.5, color="#C56A35", linestyle="--", linewidth=1.4)
axes[0].set(ylabel="Registrierte Unfälle", xlabel="Jahr", ylim=(0, 6500),
            title="Anzahl: Erfassungswechsel 2015 beachten")
axes[0].legend(frameon=False, fontsize=9, loc="upper left")
for col, label, color in [("AccidentInvolvingBicycle", "Velo (inkl. E-Bikes)", TEAL),
                           ("AccidentInvolvingPedestrian", "Fussgänger", ORANGE),
                           ("AccidentInvolvingMotorcycle", "Motorrad", GREY)]:
    axes[1].plot(participation["year"], participation[col], color="#" + color,
                 linewidth=2.6, label=label)
axes[1].set(ylabel="Anteil an Personenschadenunfällen (%)", xlabel="Jahr", ylim=(0, 50),
            title="Zusammensetzung: Beteiligung verändert sich")
axes[1].legend(frameon=False, fontsize=9, loc="upper left")
for ax in axes:
    ax.set_xticks([2011, 2015, 2020, 2025])
    chart_style(ax)
fig.tight_layout(pad=1.5, w_pad=3)
fig.savefig(ASSETS / "vortrag_f3.png", dpi=200)
plt.close(fig)

# 01 — Auftakt: bewusst keine Ergebnisbehauptung zu individuellem Risiko.
s = slide("Projektarbeit · Teil 1 · 28. Oktober 2026", "Verkehrsunfälle in Zürich", dark=True)
text(s, 0.6, 1.83, 8.5, 1.1, "Von offenen Daten zu\nnachvollziehbaren Antworten.", 29, WHITE)
text(s, 0.6, 3.4, 7.8, 0.8, "Eine reproduzierbare Python-/SQL-Pipeline\nfür registrierte Unfälle von 2011–2025.", 20, LIGHT)
for x, value, label in [(0.6, "70’767", "registrierte Unfälle"), (4.0, "15", "Unfalljahre"),
                         (7.05, "3", "Forschungsfragen")]:
    text(s, x, 5.05, 3.1, 0.75, value, 39, "79C9C1", True)
    text(s, x, 5.88, 3.1, 0.5, label, 16, LIGHT)
# Editierbares, abstraktes Strassennetz statt einer geografischen Karte.
for offset in range(4):
    rect(s, 10.75 + offset * 0.46, 1.95, 0.07, 4.35, "284653")
for yy in [2.6, 3.9, 5.2]:
    rect(s, 10.35, yy, 2.3, 0.07, "284653")
rect(s, 11.65, 3.85, 0.18, 0.18, "79C9C1", True)
text(s, 0.6, 6.55, 10.8, 0.35, "Ruben Souto · Issa Fawaz · Drin Muslija", 16, WHITE)
note(s, "Worum geht es?", 35,
     "Wir untersuchen polizeilich registrierte Verkehrsunfälle in der Stadt Zürich. "
     "Unser Ziel ist einerseits eine nachvollziehbare Data-Engineering-Pipeline und "
     "andererseits die Beantwortung von drei Forschungsfragen. Dafür verwenden wir "
     "70’767 Unfälle von 2011 bis 2025. Wir beschreiben diesen registrierten Bestand. "
     "Eine Prognose oder ein individuelles Unfallrisiko berechnen wir in Teil 1 nicht.",
     "Eine Zeile ist ein Unfall, nicht eine verletzte Person oder eine Fahrt.")

# 02 — Konzeption und Forschungsfragen.
s = slide("01 · Konzeptionalisierung", "Drei Fragen verbinden Technik und Analyse",
          "Ausgangslage: Unfälle verursachen Schäden. Offene Daten machen Muster untersuchbar.")
for x, num, title, body in [
    (0.6, "F1", "Wann?", "Tageszeit und Wochentag\n\nStundenanteile vergleichen;\nH1 prüft Unterschiede."),
    (4.72, "F2", "Mit welcher Beteiligung?", "Beteiligung und Schwere\nbei Personenschadenunfällen\n\nDrei Vergleiche; H2."),
    (8.84, "F3", "Was verändert sich?", "Anzahl und Zusammensetzung\nüber die Jahre\n\nJahresreihen und Anteile."),
]:
    card(s, x, 2.55, 3.88, 3.25, num + "  " + title, body, body_size=18)
ribbon(s, "Engineering-Ziel: dieselbe Quelle mit denselben Regeln nachvollziehbar auswerten.")
note(s, "Problemstellung und Forschungsfragen", 55,
     "Unsere drei Fragen bestimmen die Umsetzung. Erstens: Wie unterscheiden sich "
     "Unfälle nach Tageszeit und Wochentag? Zweitens: Gibt es bei Personenschadenunfällen "
     "einen Zusammenhang zwischen Beteiligung und Schwere? Drittens: Wie verändern sich "
     "Anzahl und Zusammensetzung über die Jahre? Für die ersten beiden Fragen nutzen wir "
     "Hypothesentests, für die dritte eine deskriptive Zeitreihe. Der Engineering-Beitrag "
     "ist die kontrollierte Kette von der Quelle bis zum Ergebnis. So lassen sich unsere "
     "Zahlen auf einen bestimmten Datenstand und klare Regeln zurückführen.",
     "Jede technische Komponente muss eine dieser Fragen oder die Reproduzierbarkeit unterstützen.")

# 03 — Quelle und fachlicher Umgang damit.
s = slide("02 · Datengrundlage", "Eine Zeile entspricht einem registrierten Unfall",
          "Open Data Zürich · Datenlieferant: Bundesamt für Strassen ASTRA")
card(s, 0.6, 2.45, 3.85, 3.52, "Was ist enthalten?",
     "2011–2025 · 36 Rohspalten\nZeit, Schwere, Unfallart\nBeteiligung und Koordinaten\n\n70’767 eindeutige Unfall-IDs", body_size=18)
card(s, 4.72, 2.45, 3.85, 3.52, "Bruch in der Erfassung",
     "Ab Juli 2015 werden auch\nBagatellunfälle gemeldet.\n\nGesamtzahlen über diesen\nBruch vorsichtig vergleichen.", ORANGE, 18)
card(s, 8.84, 2.45, 3.85, 3.52, "Unklare Definition",
     "Beteiligung ist im Katalog auf\nPersonenschäden bezogen;\npositive Werte auch bei\nSachschäden vorhanden.\n→ F2 nur Personenschäden.", ORANGE, 18)
ribbon(s, "Keine Daten zum Verkehrsaufkommen → keine Unfallrisiken pro Fahrt oder Kilometer.")
source(s)
note(s, "Quelle und Aussagegrenzen", 60,
     "Die Quelle stammt aus dem Open-Data-Katalog der Stadt Zürich, Datenlieferant ist "
     "das ASTRA. Der Rohbestand enthält 36 Spalten. Wichtig sind zwei fachliche Befunde. "
     "Ab Juli 2015 wurden auch Bagatellunfälle gemeldet; ein Sprung der Gesamtzahl kann "
     "deshalb durch die Erfassung entstehen. Ausserdem beschreibt der Katalog die "
     "Beteiligungsfelder mit Bezug auf Personenschäden, während auch Sachschadenzeilen "
     "positive Werte besitzen. Die Ursache haben wir nicht geklärt. Wir erhalten die "
     "Werte und beschränken F2 vorsichtig auf Personenschadenunfälle. Das ist eine "
     "begründete Abgrenzung und keine behauptete Reparatur der Quelle.",
     "Nicht registrierte Unfälle fehlen. Auffällige Daten sind nicht automatisch bewiesene Fehler.")

# 04 — Lebenszyklus vollständig inkl. Generation/Serving.
s = slide("03 · Entwurf des Lebenszyklus", "Eine lokale Batch-Pipeline mit klarer Herkunft",
          "Generation liegt ausserhalb unseres Projekts; die eigene Verarbeitung beginnt beim Bezug.")
steps = [("01", "Generation", "Polizei / ASTRA\nErfassung"),
         ("02", "Ingestion", "CSV + Metadaten\nSnapshot + Hash"),
         ("03", "Storage", "Raw-Dateien erhalten\nCSV und SQLite"),
         ("04", "Transformation", "Profil, Typen, Features\nQualitätsbericht"),
         ("05", "Serving", "SQL / Notebooks\nDiagramme und Folien")]
for i, (num, title, body) in enumerate(steps):
    x = 0.6 + i * 2.46
    rect(s, x, 2.65, 2.26, 2.28, WHITE, True)
    text(s, x + 0.18, 2.86, 1.9, 0.44, num, 24, TEAL, True)
    text(s, x + 0.18, 3.46, 1.95, 0.42, title, 18, NAVY, True)
    text(s, x + 0.18, 4.03, 1.95, 0.75, body, 14, GREY)
    if i < 4:
        text(s, x + 2.26, 3.45, 0.21, 0.4, "›", 21, TEAL, True)
rect(s, 0.6, 5.26, 12.1, 0.81, PALE, True)
text(s, 0.82, 5.43, 11.7, 0.52,
     "Unterströmungen: Sicherheit · Governance · DataOps · Orchestrierung · Software Engineering", 17)
ribbon(s, "Storage begleitet mehrere Phasen; die Reihenfolge ist kein starres Wasserfallmodell.")
note(s, "Data-Engineering-Lebenszyklus", 65,
     "Die Daten entstehen durch die polizeiliche Erfassung und das ASTRA-System. Wir "
     "übernehmen die veröffentlichten Daten als kontrollierten Snapshot. Raw-Dateien "
     "bleiben erhalten; die Transformation erzeugt eine bereinigte CSV, die wir in "
     "SQLite speichern. Die Analyse liest aus SQLite und erzeugt Ergebnisse. Die Grafik "
     "zeigt die Verantwortungen der Phasen, nicht eine starre zeitliche Reihenfolge: "
     "Speicherung findet mehrfach statt. Quer dazu laufen unter anderem Datenqualität, "
     "Sicherheit und Nachvollziehbarkeit. Die Pipeline orchestriert die Schritte und "
     "stoppt bei Fehlern. Serving bedeutet hier SQL, Notebooks und Ergebnisartefakte; "
     "ein eigener Dienst bleibt ausserhalb von Teil 1.",
     "Unser tatsächlicher Datenfluss: Download → Raw → Transformation → CSV → SQLite → Analyse.")

# 05 — Ingestion.
s = slide("04 · Ingestion", "Ein Snapshot schützt vor unbemerkten Datenwechseln",
          "Standardlauf offline · Ein neuer Download ist eine bewusste Entscheidung.")
card(s, 0.6, 2.5, 5.9, 3.35, "1  Beschaffen und festhalten",
     "Öffentliche CSV und Katalogmetadaten\nAbrufzeit, Quelle und SHA-256 speichern\nRohdaten unverändert aufbewahren\nNeue Downloads als separaten Snapshot", body_size=19)
card(s, 6.8, 2.5, 5.9, 3.35, "2  Vor der Verarbeitung prüfen",
     "Datei und Metadaten vorhanden?\nDateigrösse und Prüfsumme passend?\nCSV-Struktur und Pflichtfelder gültig?\nBei Abweichung sichtbar abbrechen.", body_size=19)
ribbon(s, "SHA-256 bestätigt Dateiintegrität – nicht die fachliche Richtigkeit der Unfalldaten.")
text(s, 0.8, 6.98, 10.6, 0.15, "Nachweis: ingestion.py · data/raw/source_metadata.json", 8, GREY)
note(s, "Ingestion und Snapshot", 45,
     "Die Ingestion beschafft die CSV und hält ihren Ursprung fest. Ein Snapshot ist "
     "eine gespeicherte Version der Quelle. Die Prüfsumme ist wie ein digitaler "
     "Fingerabdruck: Ändern sich Bytes, passt sie nicht mehr. Dadurch vermeiden wir, "
     "dass unterschiedliche Gruppenmitglieder unbemerkt verschiedene Datenstände "
     "analysieren. Der Standardlauf nutzt den vorhandenen Snapshot offline. Ein "
     "bewusster Refresh legt einen neuen Datenstand separat ab. Eine gültige Prüfsumme "
     "beweist allerdings nur Integrität, nicht, dass jede Unfallmeldung inhaltlich stimmt.",
     "Raw wird erhalten; bei einem Fehler wird nicht still ein neuer Datenstand heruntergeladen.")

# 06 — Storageentscheid.
s = slide("05 · Storage", "SQLite passt zu unserem tatsächlichen Arbeitsumfang",
          "Lokale Analyse · ein kontrollierter Schreibprozess · überwiegend lesende Abfragen")
card(s, 0.6, 2.5, 3.85, 3.3, "CSV", "Einfacher Austausch\nOriginalformat der Quelle\n\nKeine Datenbankregeln\n→ Raw und Export", GREY, 18)
card(s, 4.72, 2.5, 3.85, 3.3, "SQLite · gewählt",
     "SQL in einer portablen Datei\nPrimärschlüssel + CHECKs\nTransaktionaler Aufbau\n\nKein Serverbetrieb nötig", TEAL, 18)
card(s, 8.84, 2.5, 3.85, 3.3, "PostgreSQL",
     "Zentraler Mehrnutzerbetrieb\nViele parallele Schreibzugriffe\n\nDafür wären Server und\nBetrieb zusätzlich nötig.", GREY, 18)
ribbon(s, "Relational: feste Spalten, eindeutige Unfall-ID und SQL-Aggregationen für F1–F3.")
source(s, "Begründung: sqlite.org/whentouse.html · Schema: src/de_projekt/schema.sql")
note(s, "Warum SQLite?", 60,
     "Wir haben CSV, SQLite und PostgreSQL verglichen. CSV bewahrt das Originalformat, "
     "bietet aber keine Datenbank-Constraints. SQLite erlaubt SQL, eindeutige Schlüssel "
     "und geprüfte Wertebereiche in einer einzigen Datei. Für 70’767 Zeilen mit einem "
     "kontrollierten Ladeprozess und anschliessenden Leseanalysen reicht das aus. "
     "PostgreSQL wäre eine Option bei einer zentralen Datenbank mit vielen parallelen "
     "Schreibzugriffen. Diese Anforderung haben wir nicht. Jedes Teammitglied nutzt "
     "eine lokale Kopie; wir bearbeiten nicht gleichzeitig eine geteilte SQLite-Datei. "
     "Die relationale Struktur passt, weil jede Zeile einen Unfall mit fester ID und "
     "vergleichbaren Merkmalen beschreibt.",
     "SQLite ist eine Datenbank, keine Excel-Datei. Auswahl nach Bedarf begründen, nicht nach Prestige.")

# 07 — Transformation und nachweisbare Regeln.
s = slide("06 · Transformation Teil 1", "Bereinigen heisst auch: begründet nichts löschen",
          "Profilbefund: keine leeren Felder, geprüften NA-Marker oder Duplikate im Snapshot.")
card(s, 0.6, 2.45, 5.9, 3.56, "Von 36 auf 22 Spalten",
     "19 Originalfelder + 3 neue Merkmale\nExplizite Zahlen-, Text- und boolesche Typen\nSprachredundanzen nur im Export entfernen\nKeine Zeilen löschen, nichts imputieren\nUnbekannt bleibt NULL; ungültig → Abbruch", body_size=18)
card(s, 6.8, 2.45, 5.9, 3.56, "Drei nachvollziehbare Features",
     "is_weekend: Samstag / Sonntag\ntime_period: vier Sechs-Stunden-Blöcke\nvulnerable_road_user: Fussgänger ODER Velo\n\nH1 nutzt Wochenende × Originalstunde;\ndie anderen Features ergänzen den Bestand.", body_size=18)
ribbon(s, "70’767 hinein → 70’767 hinaus · Regeln und Prüfsummen stehen im Qualitätsbericht.")
note(s, "Datenprofil, Bereinigung und Features", 60,
     "Das Datenprofil untersucht zunächst Qualität und Wertebereiche. Im aktuellen "
     "Snapshot fehlen keine Felder und es gibt keine doppelten Unfall-IDs. Deshalb "
     "löschen wir keine Zeilen und erfinden keine fehlenden Werte. Wir wählen 19 "
     "Originalfelder, setzen Datentypen und ergänzen drei Merkmale. is_weekend fasst "
     "Samstag und Sonntag zusammen; time_period bildet vier Sechs-Stunden-Blöcke. "
     "vulnerable_road_user verknüpft Fussgänger- oder Velobeteiligung. Das letzte "
     "Merkmal ist eine ergänzende Gruppierung und kein eigener Test im aktuellen "
     "Ergebnis. Die Rohdaten enthalten weiterhin alle Originalspalten. Ein "
     "Qualitätsbericht dokumentiert Auswahl, Regeln und unveränderte Fallzahl.",
     "Bereinigung kann Typisierung und Validierung bedeuten. 0 bedeutet nein, NULL bedeutet unbekannt.")

# 08 — Hypothesen und Methoden.
s = slide("07 · Methoden", "Wir testen Zusammenhänge und berichten ihre Stärke",
          "Pearson-Chi-Quadrat · α = 0,05 · Cramérs V ergänzt den p-Wert")
card(s, 0.6, 2.45, 5.9, 3.53, "H1 · Zeitliche Verteilung",
     "H0: Gleiche Stundenverteilung an\nWerktagen und Wochenenden.\nAlternative: unterschiedliche Verteilung.\n\nTabelle: 2 Gruppen × 24 Stunden\nAlle 70’767 Unfälle", body_size=18)
card(s, 6.8, 2.45, 5.9, 3.53, "H2 · Beteiligung und Schwere",
     "H0: Beteiligung und Schwere unabhängig.\nAlternative: ein Zusammenhang besteht.\nDrei Tests: Fussgänger, Velo, Motorrad\n\nJe 2 × 3 Zellen · 18’164 Personenschäden\nHolm korrigiert die drei p-Werte.", body_size=18)
ribbon(s, "Erwartete Zellen alle > 5; zeitliche Unabhängigkeit bleibt eine Modellannahme.")
source(s, "Methode: SciPy chi2_contingency · Holm (1979), Scandinavian Journal of Statistics 6(2), 65–70")
note(s, "Hypothesen und Testlogik", 65,
     "Der Chi-Quadrat-Test vergleicht beobachtete Häufigkeiten mit den Häufigkeiten, "
     "die unter der Nullhypothese zu erwarten wären. Bei H1 sind das zwei Gruppen "
     "und 24 Stunden. Bei H2 prüfen wir je Beteiligungsmerkmal zwei Gruppen und "
     "drei Schweregrade: leicht, schwer und tödlich. Ein Unfall zählt pro Test genau "
     "einmal, darf aber mehrere Beteiligungsmerkmale haben. Weil wir bei H2 drei "
     "Tests durchführen, verwenden wir Holm zur Korrektur der p-Werte. Der p-Wert "
     "beschreibt die Vereinbarkeit mit dem Modell; Cramérs V die Stärke der "
     "beobachteten Assoziation. Alle erwarteten Zellen sind ausreichend gross, "
     "aber zeitliche Abhängigkeiten können die Modellinterpretation begrenzen.",
     "p < 0,05 beweist weder eine Ursache noch eine grosse praktische Bedeutung.")

# 09 — F1.
s = slide("08 · Ergebnis F1", "Am Wochenende verlagert sich die Stundenverteilung",
          "Relative Anteile innerhalb jeder Gruppe; kein blosser Vergleich von fünf mit zwei Tagen.")
rect(s, 0.6, 2.43, 8.2, 3.8, WHITE, True)
picture(s, ASSETS / "vortrag_f1.png", 0.69, 2.49, 8.02, 3.66)
card(s, 9.03, 2.43, 3.67, 3.8, "Nacht · 00–05 Uhr",
     "3,71 %  werktags\n14,63 %  am Wochenende\n\nSpitzenstunde: 17 / 14 Uhr\np < 0,001 · V = 0,234\nH0 wird verworfen.", body_size=17)
ribbon(s, "Befund: andere Verteilung registrierter Unfälle; kein höheres Risiko pro Wochenendfahrt.")
source(s)
note(s, "F1: Tageszeit und Wochentag", 65,
     "Die Kurven summieren sich innerhalb der jeweiligen Gruppe auf 100 Prozent. "
     "Damit vergleichen wir die Form der Stundenverteilung und nicht einfach "
     "fünf Werktage mit zwei Wochenendtagen. Werktags liegt die häufigste Stunde "
     "bei 17 Uhr, am Wochenende bei 14 Uhr. Zwischen Mitternacht und fünf Uhr "
     "liegen 3,71 Prozent der Werktagsunfälle und 14,63 Prozent der Wochenendunfälle. "
     "Der Unterschied ist im verwendeten Test signifikant; Cramérs V beträgt 0,234. "
     "Das Muster eines höheren Nachtanteils am Wochenende sehen wir deskriptiv "
     "in allen 15 Jahren. Wir wissen damit aber nicht, wie hoch das Risiko einer "
     "einzelnen Fahrt ist, weil uns die Zahl und Länge der Fahrten fehlen.",
     "Die Nenner sind alle Werktagsunfälle beziehungsweise alle Wochenendunfälle.")

# 10 — F2.
s = slide("09 · Ergebnis F2", "Beteiligung hängt mit der Unfallschwere zusammen",
          "Nur Personenschadenunfälle · Gezeigt: schwer / tödlich zur verständlichen Einordnung.")
rect(s, 0.6, 2.43, 8.2, 3.8, WHITE, True)
picture(s, ASSETS / "vortrag_f2.png", 0.69, 2.49, 8.02, 3.66)
card(s, 9.03, 2.43, 3.67, 3.8, "Alle drei signifikant",
     "Nach Holm-Korrektur\nCramérs V:\nFussgänger  0,104\nVelo               0,054\nMotorrad        0,036\n→ Kleine Assoziationen", body_size=17)
ribbon(s, "Der Test nutzt drei Schweregrade. Beteiligung sagt nicht, welche Person verletzt wurde.", size=16)
source(s)
note(s, "F2: Beteiligung und Unfallschwere", 65,
     "Für diese Frage betrachten wir 18’164 Personenschadenunfälle. Die Balken "
     "zeigen zur Interpretation den Anteil schwerer oder tödlicher Unfälle. "
     "Mit Fussgängerbeteiligung sind es 23,42 Prozent, ohne 15,02 Prozent. Auch "
     "bei Velo und Motorrad liegen die dargestellten Anteile mit Beteiligung höher. "
     "Die eigentlichen Tests verwenden alle drei Schweregrade getrennt. Alle "
     "drei Ergebnisse sind nach Holm signifikant, die Effektgrössen sind aber "
     "numerisch klein. Ein Unfall kann mehrere Beteiligungsmerkmale besitzen. "
     "Die Schwere gehört zum gesamten Unfall; wir können nicht daraus ableiten, "
     "wer verletzt wurde oder dass eine bestimmte Beteiligung den Schaden verursacht.",
     "F2 beschreibt Unfälle, nicht die Gefährlichkeit einer Verkehrsart pro Kilometer.")

# 11 — F3.
s = slide("10 · Ergebnis F3", "Anzahl und Zusammensetzung verändern sich",
          "Eine Zeitreihe zeigt mehr als der Vergleich des ersten mit dem letzten Jahr.")
rect(s, 0.6, 2.43, 12.1, 3.8, WHITE, True)
picture(s, ASSETS / "vortrag_f3.png", 0.72, 2.5, 11.86, 3.63)
ribbon(s, "2016 → 2025: total 5’556 → 4’714 · Personenschäden 1’262 → 1’310 · keine stetige Zunahme.", size=16)
source(s)
note(s, "F3: Zeitliche Veränderung", 65,
     "Links stehen die jährlichen Fallzahlen. Die gestrichelte Linie markiert "
     "den bekannten Erfassungswechsel 2015. Der Höchststand liegt 2018, daher "
     "wäre die Aussage einer stetigen Zunahme falsch. Zwischen 2016 und 2025 "
     "sinken die Gesamtzahlen von 5’556 auf 4’714; Personenschadenunfälle steigen "
     "im selben Vergleich leicht von 1’262 auf 1’310. Rechts sehen wir die "
     "Beteiligungsanteile innerhalb der Personenschadenunfälle. Der Veloanteil "
     "steigt von 26,12 Prozent im Jahr 2011 auf 40,38 Prozent im Jahr 2025. "
     "Das ist eine Veränderung der Zusammensetzung. Ohne Verkehrsleistung "
     "können wir daraus keine Veränderung des Risikos beim Velofahren ableiten. "
     "Die Beteiligungsanteile sind wegen Mehrfachbeteiligung nicht additiv.",
     "Personenschadenunfälle sind Unfallzahlen, keine Zahl verletzter Personen.")

# 12 — Funktionalität und Grenzen.
s = slide("11 · Qualität und Grenzen", "Technisch geprüft, fachlich bewusst begrenzt",
          "Reproduzierbarkeit sichert den Rechenweg. Sie beseitigt keine Grenzen der Quelle.")
card(s, 0.6, 2.45, 5.9, 3.55, "Was ist abgesichert?",
     "43 Tests und Codeprüfung erfolgreich\nPipeline + beide Notebooks erneut geprüft\nErgebnisse im isolierten Lauf reproduziert\nPrüfsummen und SQLite-Integrität geprüft\nFehlerfälle: ungültige Werte, IDs, Metadaten", body_size=18)
card(s, 6.8, 2.45, 5.9, 3.55, "Was bleibt offen?",
     "Dunkelziffer nicht registrierter Unfälle\nKeine Verkehrsleistung / Expositionsdaten\nKeine kausale oder adjustierte Analyse\nMögliche zeitliche Abhängigkeiten\nErfassungsbruch und Definitionsdiskrepanz", ORANGE, 18)
ribbon(s, "Nachvollziehbare Schlussfolgerungen statt unbelegter Risiko- oder Ursachenbehauptungen.")
note(s, "Funktionalität und fachliche Grenzen", 45,
     "Die technische Prüfung umfasst 43 automatisierte Tests, die Codeprüfung, "
     "die Pipeline und beide Notebooks. Ein isolierter Neulauf erzeugt dieselben "
     "fachlichen Ergebnisse. Die Datenbank wird vor dem Austausch geprüft. "
     "Das zeigt, dass unser Verfahren funktioniert. Es beweist aber nicht, dass "
     "die Quelldaten alle tatsächlichen Unfälle enthalten oder dass unsere "
     "Zusammenhänge kausal sind. Es fehlen Verkehrsleistung und weitere "
     "Einflussgrössen. Daher bleiben die Aussagen auf den registrierten Bestand "
     "und das verwendete Modell begrenzt.",
     "Tests prüfen Programmverhalten; sie sind keine Garantie für vollständige oder wahre Quelldaten.")

# 13 — Zusammenfassung.
s = slide("12 · Antworten auf die Forschungsfragen", "Drei Antworten auf einer nachvollziehbaren Grundlage",
          "Der Mehrwert liegt in fachlich eingeordneten Ergebnissen und einer überprüfbaren Verarbeitung.")
for yy, num, heading, body in [
    (2.48, "F1", "Zeitmuster unterscheiden sich.", "Am Wochenende liegt ein deutlich höherer Anteil der registrierten Unfälle in der Nacht."),
    (3.72, "F2", "Beteiligung und Schwere sind assoziiert.", "Alle drei Vergleiche sind signifikant; kleine Effektgrössen, keine Kausalaussage."),
    (4.96, "F3", "Der Bestand verändert sich uneinheitlich.", "Gesamtzahl und Personenschäden entwickeln sich unterschiedlich; der Veloanteil nimmt zu."),
]:
    rect(s, 0.6, yy, 12.1, 1.06, WHITE, True)
    text(s, 0.82, yy + 0.18, 0.7, 0.53, num, 24, TEAL, True)
    text(s, 1.75, yy + 0.12, 10.5, 0.4, heading, 21, NAVY, True)
    text(s, 1.75, yy + 0.59, 10.5, 0.36, body, 16, GREY)
ribbon(s, "Teil 1: Datengrundlage, initiale Transformation und Analyse · kein Machine Learning.")
note(s, "Kernaussagen zusammenführen", 40,
     "Zusammenfassend unterscheiden sich die zeitlichen Muster zwischen "
     "Werktagen und Wochenenden. Beteiligung und Schwere stehen bei "
     "Personenschadenunfällen in einem statistischen Zusammenhang, dessen "
     "Stärke wir einordnen müssen. Die jährliche Entwicklung ist nicht "
     "einheitlich; besonders der Erfassungswechsel verhindert einfache "
     "Schlussfolgerungen aus Gesamtzahlen. Die Pipeline schafft dafür eine "
     "überprüfbare Grundlage von der Quelle bis zur Antwort. Das ist unser "
     "Ergebnis von Teil 1.",
     "Die fachliche Aussage und die technische Grundlage gehören zusammen.")

# 14 — Schlussfolie mit konkreter Abgabe statt versprochenem Dienst.
s = slide("13 · Reproduzierbarkeit und Abgabe", "Vom Ergebnis zurück zur Quelle – jede Stufe ist vorhanden", dark=True)
for x, title, body in [(0.6, "Verstehen", "README\nKonzept und Entscheidungen\nAusgeführte Notebooks"),
                       (4.72, "Nachvollziehen", "Python-Code und SQL-Schema\nRaw + Metadaten\nCSV + SQLite + Berichte"),
                       (8.84, "Prüfen", "43 Tests und Codeprüfung\nDokumentierte Ausführung\nGit-Branch: abgabe/teil1")]:
    rect(s, x, 2.65, 3.85, 2.68, "1C3B49", True)
    text(s, x + 0.22, 2.87, 3.4, 0.5, title, 23, "79C9C1", True)
    text(s, x + 0.22, 3.58, 3.4, 1.5, body, 18, WHITE)
text(s, 0.6, 5.9, 11.9, 0.65, "Fragen?", 34, WHITE, True)
text(s, 0.6, 6.65, 11.9, 0.3, "Teil 2: Erweiterungen erst auf separatem Arbeitsstand.", 15, LIGHT)
note(s, "Abschluss und Nachweise", 25,
     "Die Abgabe enthält die Präsentation sowie den Code, die Originaldaten, "
     "den bereinigten Bestand, die Datenbank und die ausgeführten Analysen. "
     "Das README erklärt den Einstieg. Der separate Abgabebranch hält den "
     "geprüften Stand für Teil 1 fest. Erweiterungen für Teil 2 erfolgen "
     "getrennt davon. Vielen Dank, wir beantworten gerne Fragen.",
     "Ein eingefrorener Branch ist eine Arbeitsvereinbarung; der genaue Commit identifiziert den Stand.")

# 15–18 — Reserve, nicht Teil der Standardvortragszeit.
s = slide("Reserve A · Datenbank und SQL", "Eine Unfalltabelle genügt für unsere Fragen",
          "accidents: 70’767 Zeilen · 22 Spalten · AccidentUID als Primärschlüssel")
card(s, 0.6, 2.45, 4.0, 3.55, "Datenmodell",
     "Zeit und Schwere\nUnfall- und Strassenart\nBeteiligungsmerkmale\nKoordinaten + 3 Features\n\npipeline_metadata:\nHerkunft und Regelversionen", body_size=16)
rect(s, 4.9, 2.45, 7.8, 3.55, NAVY, True)
text(s, 5.16, 2.75, 7.3, 2.8,
     "SELECT AccidentYear, COUNT(*) AS n\nFROM accidents\nWHERE AccidentSeverityCategory\n      IN ('as1', 'as2', 'as3')\nGROUP BY AccidentYear\nORDER BY AccidentYear;", 19, WHITE, font="Consolas")
ribbon(s, "STRICT-Typen · CHECK-Regeln · transaktionaler Aufbau · Integritäts- und Wertevergleich")
note(s, "Reserve: Datenmodell und SQL", 0,
     "Eine Tabelle reicht, weil unsere Beobachtungseinheit der Unfall ist und "
     "wir keine eigenen Personen- oder Fahrzeugdatensätze besitzen. Der "
     "Primärschlüssel verhindert doppelte IDs. CHECK-Regeln prüfen Wertebereiche "
     "und die Konsistenz berechneter Features. pipeline_metadata dokumentiert "
     "die Herkunft. Das SQL-Beispiel zählt Personenschadenunfälle pro Jahr. "
     "Die Tabelle ist relational nutzbar, auch ohne mehrere Dimensionstabellen.",
     "Die Datei accidents.sqlite reicht zum Öffnen; Code und Rohdaten sind für Reproduktion nötig.")

s = slide("Reserve B · Testdetails", "Signifikanz, Effektgrösse und Fallzahl gemeinsam lesen",
          "Pearson-Chi-Quadrat ohne Kontinuitätskorrektur · H1 separat, H2 als Familie korrigiert")
rows = [("H1 · Zeit", "70’767", "3’877,063", "23", "< 0,001", "0,234"),
        ("H2 · Fussgänger", "18’164", "194,879", "2", "1,444 × 10⁻⁴²", "0,104"),
        ("H2 · Velo", "18’164", "52,602", "2", "7,563 × 10⁻¹²", "0,054"),
        ("H2 · Motorrad", "18’164", "23,961", "2", "6,267 × 10⁻⁶", "0,036")]
cols = [(0.8, 2.55), (3.3, 1.25), (4.65, 1.6), (6.37, 0.6), (7.2, 2.8), (10.3, 1.6)]
for (x, w), heading in zip(cols, ["Test", "n", "χ²", "df", "p / p(Holm)", "Cramérs V"]):
    text(s, x, 2.47, w, 0.5, heading, 17, TEAL, True)
for i, row in enumerate(rows):
    yy = 3.15 + i * 0.64
    rect(s, 0.6, yy - 0.08, 12.1, 0.59, WHITE if i % 2 == 0 else PALE)
    for (x, w), value in zip(cols, row):
        text(s, x, yy, w, 0.43, value, 17)
ribbon(s, "Kleinste erwartete Zelle: H1 114,61 · H2 mindestens 15,59. H1-p-Wert numerisch unterlaufen.")
source(s, "Nachweis: data/processed/analysis_summary.json · hypothesis_tests_h2.csv · analysis.py")
note(s, "Reserve: Zahlen und Testannahmen", 0,
     "Der H1-p-Wert wird als kleiner als 0,001 berichtet, weil die "
     "Gleitkommaberechnung auf null unterläuft. Er ist nicht mathematisch null. "
     "Bei H2 zeigt die Tabelle die Holm-korrigierten Werte. Cramérs V lässt "
     "die Grössenordnung der Assoziation erkennen. Alle erwarteten Häufigkeiten "
     "liegen über fünf. Dies stützt die asymptotische Berechnung, beweist aber "
     "nicht die zeitliche Unabhängigkeit oder Kausalität.",
     "df sind Freiheitsgrade; für eine R×C-Tabelle gilt (R−1)×(C−1).")

s = slide("Reserve C · Unterströmungen und Erweiterbarkeit", "Qualität und Verantwortung begleiten jede Phase",
          "Eine einfache Architektur kann klare Kontrollen besitzen und später erweitert werden.")
for x, yy, title, body in [
    (0.6, 2.45, "Sicherheit & Governance", "Öffentliche Daten, keine Secrets\nQuelle, Lizenz und Snapshot dokumentiert"),
    (6.8, 2.45, "DataOps & Qualität", "Tests, Prüfsummen und Qualitätsberichte\nSichtbarer Abbruch bei Fehlern"),
    (0.6, 4.22, "Orchestrierung & Engineering", "Getrennte Module; explizite Pfadübergaben\nGit-Versionierung und reproduzierbarer Lauf"),
    (6.8, 4.22, "Architektur & Skalierbarkeit", "Bei grösseren Daten: chunkweise Verarbeitung\nBei zentralem Mehrnutzerbedarf: PostgreSQL"),
]:
    rect(s, x, yy, 5.9, 1.52, WHITE, True)
    text(s, x + 0.2, yy + 0.15, 5.5, 0.4, title, 19, TEAL, True)
    text(s, x + 0.2, yy + 0.69, 5.5, 0.67, body, 16)
ribbon(s, "Skalierung ist ein begründeter Erweiterungsweg; keine bereits getestete Serverarchitektur.")
note(s, "Reserve: Unterströmungen und Skalierung", 0,
     "Nachvollziehbarkeit entsteht durch dokumentierte Herkunft, Regeln und "
     "Versionen. Fehler stoppen die Verarbeitung. Die lokale Batch-Pipeline "
     "passt zur jährlich veröffentlichten Quelle. Für erheblich grössere Daten "
     "könnten wir chunkweise arbeiten; für eine zentrale Datenbank mit vielen "
     "Schreibzugriffen wäre PostgreSQL neu zu evaluieren. Diese Möglichkeiten "
     "sind ein Entwurf, keine nachgewiesene Lastskalierung. Die öffentliche "
     "Quelle wird nicht zur Identifizierung beteiligter Personen verknüpft.",
     "Eine geplante Erweiterung nicht als bereits implementierte Funktion darstellen.")

s = slide("Reserve D · Quellen und Hilfsmittel", "Quellen, Regeln und Unterstützung offenlegen",
          "Die fachliche Verantwortung und die mündliche Erklärung liegen beim Projektteam.")
items = [
    ("Daten", "Open Data Zürich · Bundesamt für Strassen ASTRA\nSnapshot vom 13.10.2026; Lizenz laut Katalog: Creative Commons Attribution"),
    ("Datenbank", "SQLite: Appropriate Uses For SQLite\nhttps://www.sqlite.org/whentouse.html"),
    ("Statistik", "SciPy: scipy.stats.chi2_contingency · docs.scipy.org\nHolm (1979): A Simple Sequentially Rejective Multiple Test Procedure, 6(2), 65–70"),
    ("Hilfsmittel", "OpenAI Codex / ChatGPT: Unterstützung bei Code, Dokumentation, Prüfung und Folien\nPython, Pandas, SciPy, Matplotlib, SQLite; Folien: python-pptx und PowerPoint"),
]
for i, (title, body) in enumerate(items):
    yy = 2.37 + i * 1.02
    text(s, 0.7, yy, 1.85, 0.45, title, 18, TEAL, True)
    text(s, 2.63, yy, 9.8, 0.81, body, 15)
text(s, 0.7, 6.6, 11.9, 0.3,
     "Vollständige Daten-URL und Nachweise: README sowie docs/abgabe_teil1.md", 13, GREY)
note(s, "Reserve: Quellen und Hilfsmittel", 0,
     "Die Datenquelle wird mit ASTRA als Datenlieferant angegeben. SQLite und "
     "SciPy sind durch offizielle Dokumentation belegt. Die Holm-Korrektur "
     "folgt der Veröffentlichung von 1979. KI-Unterstützung ist offengelegt: "
     "Sie wurde für Implementierung, Dokumentation, Prüfung und Präsentation "
     "verwendet. Eine kursspezifische Erklärung ist gegebenenfalls zusätzlich "
     "nach dessen Vorgaben einzureichen; solche Vorgaben liegen uns nicht vor.",
     "Nur persönlich geprüfte und verstandene Arbeit als eigene Erklärung vertreten.")

prs.save(OUT / "teil1_verkehrsunfaelle_zuerich.pptx")

guide = """# Vorbereitung auf die Präsentation – Teil 1

Die Präsentation hat **14 Hauptfolien und 4 Reservefolien**. Die Richtzeiten
ergeben ungefähr 13 Minuten; sie sind eine Planung, keine vorgegebene Kursdauer.
Bei 10 Minuten Folien 3 und 5 sowie die Methodenfolie knapper erklären; keine
Reservefolien durchgehen. Bei 15 Minuten etwas Zeit für Übergänge lassen.
PowerPoint enthält denselben Sprechtext in den Notizen. Die PDF enthält die
Folien, keine Sprechernotizen. Du musst den Text nicht auswendig lernen.

## Zuerst diese Erklärung verstehen

Wir haben einen veröffentlichten Datenbestand über registrierte Unfälle in Zürich
festgehalten. Python prüft die Quelle, setzt Datentypen und ergänzt verständliche
Merkmale. Die aufbereiteten Unfälle liegen in einer SQLite-Datenbank. Notebooks
lesen daraus und zeigen zeitliche Muster, Zusammenhänge mit der Schwere und
Veränderungen über die Jahre. Wir können die Verarbeitung wiederholen und jede
Zahl auf die Quelle zurückführen. Wir berechnen keine individuellen Risiken.

## Vorbereitung mit wenig Zeit

1. **10 Minuten:** Folien 1–7 ansehen. Den Datenfluss laut in eigenen Worten erklären.
2. **15 Minuten:** Folien 8–13 ansehen. Zu jedem Diagramm Frage, Nenner, Ergebnis und Grenze sagen.
3. **10 Minuten:** Die Fragen unten beantworten und unsichere Begriffe nachlesen.
4. **15 Minuten:** Einmal mit Zeitmessung vollständig vortragen. Folien abkürzen statt schneller reden.
5. Vor dem Vortrag PPTX und PDF lokal öffnen. Den Vortrag ohne Live-Demo durchführen.

## Mögliche Aufteilung im Dreierteam

- Person A: Folien 1–5 (Problem, Daten, Lebenszyklus, Ingestion).
- Person B: Folien 6–8 (Storage, Transformation, Methoden).
- Person C: Folien 9–14 (Ergebnisse, Grenzen, Abschluss).

Dies ist ein Vorschlag, keine bestätigte Teamabsprache. Jeder sollte den gesamten
Datenfluss, die SQLite-Begründung und die drei Ergebnisgrenzen erklären können.

## Sprechhilfe je Folie

"""
for i, (title, seconds, speech, understand) in enumerate(NOTES, 1):
    timing = f"ca. {seconds} Sekunden" if seconds else "nur bei Rückfragen"
    guide += f"### Folie {i}: {title} ({timing})\n\n{speech}\n\n**Merken:** {understand}\n\n"
guide += """## Typische Fragen mit kurzen Antworten

**Was habt ihr konkret gebaut?** Eine reproduzierbare lokale Batch-Pipeline:
Raw-Snapshot → Python-Prüfung und Transformation → CSV und SQLite → SQL-/Pandas-Analyse.
Dazu Herkunftsmetadaten, Qualitätsberichte, Tests und ausgeführte Notebooks.

**Warum keine andere Datenbank?** SQLite erfüllt unseren lokalen Analysebedarf
mit SQL und Constraints ohne Serverbetrieb. PostgreSQL wäre bei zentralem
Mehrnutzerbetrieb mit vielen gleichzeitigen Schreibzugriffen neu zu evaluieren.
Alle arbeiten mit lokalen Kopien, nicht gleichzeitig auf derselben DB-Datei.

**Braucht es nicht mehrere Tabellen, damit es relational ist?** Nein. Die
Unfalltabelle hat feste Attribute, Datentypen und einen eindeutigen Schlüssel.
Es gibt keine separaten Personen-/Fahrzeugdatensätze, die wir sinnvoll auslagern
könnten. Weitere Tabellen nur für tatsächlich vorhandene Beziehungen aufbauen.

**Was bedeutet Bereinigung, wenn ihr nichts löscht?** Wir prüfen die Qualität,
setzen Typen, wählen relevante Felder und ergänzen Features. Keine fehlenden Werte
oder Duplikate gefunden heisst: keine unbegründete Löschung oder Imputation.

**Was heisst Feature?** Eine abgeleitete Spalte, zum Beispiel Samstag/Sonntag →
is_weekend. Das ist noch kein Machine Learning. time_period und vulnerable_road_user
sind ergänzende Merkmale; die primären Tests verwenden sie nicht als eigene Faktoren.

**Was ist der Unterschied zwischen Raw, CSV und SQLite?** Raw bewahrt das Original;
die bereinigte CSV ist ein Austauschformat. SQLite enthält denselben aufbereiteten
Bestand mit Typen, Schlüssel und Datenbankregeln für SQL-Abfragen.

**Wie vermeidet ihr doppelte Daten bei einem Neulauf?** Eine neue Datenbank wird
temporär aufgebaut, mit dem CSV-Bestand verglichen und geprüft. Erst dann wird
die alte Datei ersetzt; Unfälle werden nicht bei jedem Lauf angehängt.

**Wie funktioniert Chi-Quadrat?** Er vergleicht beobachtete mit unter der
Nullhypothese erwarteten Häufigkeiten. Erwartet = Zeilensumme × Spaltensumme / n.
Die Statistik summiert (beobachtet − erwartet)² / erwartet über alle Zellen.

**Was bedeutet p < 0,05?** Unter Nullhypothese und Testannahmen wäre ein mindestens
so stark abweichendes Ergebnis entsprechend selten. Es bedeutet nicht, dass die
Nullhypothese mit 5 Prozent Wahrscheinlichkeit wahr ist. Es beweist keine Ursache.

**Warum Holm?** Drei H2-Tests erhöhen die Chance zufälliger Zurückweisungen.
Holm korrigiert die p-Werte innerhalb dieser Familie. H1 behandeln wir separat.

**Was ist Cramérs V?** Eine normierte Assoziationsstärke aus der Chi-Quadrat-Statistik.
0 entspricht keiner gemessenen Assoziation; grössere Werte bedeuten stärkere
Assoziation. Unsere H2-Werte sind klein, trotz kleiner p-Werte und grosser Fallzahl.

**Warum nur Personenschäden für H2?** Die Katalogbeschreibung der Beteiligung ist
mit den positiven Sachschadenangaben nicht eindeutig vereinbar. Wir verändern
diese Werte nicht, sondern begrenzen die Frage ausdrücklich auf Personenschäden.

**Ist Velofahren gefährlicher geworden?** Das lässt sich aus diesen Daten nicht
beantworten. Der Veloanteil an Personenschadenunfällen steigt. Wir wissen nicht,
wie viele Fahrten oder Kilometer die Verkehrsarten zurückgelegt haben.

**Sind am Wochenende mehr Unfälle?** Unsere H1 beantwortet eine andere, genaue
Frage: Die Stundenverteilung innerhalb der Werktags-/Wochenendgruppe unterscheidet
sich. Sie testet weder Tagesraten noch Risiken pro Fahrt.

**Warum darf man Jahreszahlen nicht einfach vergleichen?** Ab Juli 2015 änderte
sich die Erfassung von Sachschäden. Ein Unterschied kann aus der Meldung entstehen.
Wir zeigen die ganze Reihe und unterscheiden Personen- von Sachschäden.

**Was kann das Projekt nicht?** Nicht registrierte Unfälle erfassen, individuelle
Risiken berechnen oder Ursachen nachweisen. Jahr, Wetter, Infrastruktur und
Verkehrsleistung sind im primären Test nicht gemeinsam kontrolliert.

**Warum keine Cloud oder Echtzeitpipeline?** Die Quelle wird jährlich publiziert;
die lokale Datenmenge ist überschaubar. Batch-Verarbeitung erfüllt den Bedarf.

**Was habt ihr mit KI gemacht?** KI unterstützte Code, Dokumentation, Prüfung und
Folien. Das wird offengelegt. Das Team muss die Inhalte verstehen und selbst
vertreten; individuelle Beiträge und eine mögliche Kurserklärung nicht erfinden.

## Vier Dateien, die du zeigen können solltest

- `README.md`: Konzept, Entscheidungen und Ausführung.
- `src/de_projekt/pipeline.py`: verbindet Ingestion, Transformation und Speicherung.
- `src/de_projekt/schema.sql`: Tabellen, Primärschlüssel und CHECK-Regeln.
- `notebooks/02_analyse.ipynb`: SQL-Abfragen, Diagramme und Hypothesentests.

## Wenn du bei einer Rückfrage unsicher bist

Bleibe bei der belegten Aussage: „Das haben wir in Teil 1 nicht untersucht.“
oder „Unsere Daten zeigen diesen Zusammenhang, aber keine Ursache.“ Keine
Technologiekenntnisse oder eigenen Codebeiträge behaupten, die du nicht erklären kannst.
"""
(OUT / "vorbereitung_teil1.md").write_text(guide, encoding="utf8")
print(f"Erstellt: {len(prs.slides)} Folien, Notizen, Lernleitfaden und 3 Diagramme.")
print(f"Geplante Hauptvortragszeit: {sum(n[1] for n in NOTES) / 60:.1f} Minuten")
