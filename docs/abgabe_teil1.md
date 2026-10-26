# Abgabe Teil 1 – Einstieg und Abschlussprüfung

Abschlussstand: **26. Oktober 2026**. Abgabefrist laut übermittelter Aufgabe:
**27. Oktober 2026, 23:59 Uhr**; Präsentation am **28. Oktober 2026**.
Branch: **`abgabe/teil1`** im gemeinsamen GitHub-Repository.

## Direkt öffnen

- [PowerPoint mit Sprechernotizen](../presentations/teil1_verkehrsunfaelle_zuerich.pptx)
- [PDF der Folien](../presentations/teil1_verkehrsunfaelle_zuerich.pdf)
- [Vorbereitung und Antworten auf Rückfragen](../presentations/vorbereitung_teil1.md)
- [README: Konzept, Begründungen, Ausführung und SQL-Beispiele](../README.md)
- [Datenprofil](../notebooks/01_datenprofil.ipynb) und [Analyse](../notebooks/02_analyse.ipynb)
- [SQLite-Datenbank](../data/processed/accidents.sqlite)

Die PowerPoint enthält **14 Hauptfolien und 4 Reservefolien**. Geplante Sprechzeit:
etwa **12–15 Minuten**, nicht als vorgegebene Kursdauer zu verstehen. In PowerPoint
über „Notizen“ bzw. die Referentenansicht den Sprechtext anzeigen. Die PDF enthält
die 18 Folien, keine Notizen. Die Vorbereitung ist eine Lernhilfe für das Team.

## Festgelegter Umfang

Die Aufgabenfolie verlangt für die grünen Inhalte eine Präsentation und für die
blauen Inhalte zusätzlich technische Artefakte. Die Abgabe enthält deshalb den
ausführbaren Projektstand einschliesslich Originaldaten und Datenbank, die
ausgeführten Notebooks sowie die Präsentation. Das ist eine begründete Auslegung
der übermittelten Aufgabe, keine zusätzliche Vorgabe der Hochschule.

SQLite bleibt gewählt: rund 70’000 strukturierte Zeilen, ein kontrollierter
Ladeprozess und lokale Leseanalysen benötigen keinen Datenbankserver. Jede Person
nutzt eine lokale Kopie. Eine gemeinsam über ein Netzlaufwerk bearbeitete Datei
ist nicht die Architektur. PostgreSQL wurde als Alternative evaluiert und bleibt
bei zentralem Mehrnutzerbedarf eine Erweiterungsoption. Begründung:
[offizielle SQLite-Dokumentation](https://www.sqlite.org/whentouse.html).

Kein Machine Learning, keine neue Datenquelle, keine Änderung der Hypothesen nach
Betrachtung der Ergebnisse und kein eigener Serving-Dienst werden für Teil 1
ergänzt. Das historische [fachliche Review](fachliches_review_teil1.md) bleibt als
interner Nachweis erhalten; es ist keine zusätzliche Pflichtabgabe und keine
unabhängige Begutachtung durch eine externe Person.

## Zuordnung zur Aufgabenfolie

| Bereich | Präsentation | Technischer / schriftlicher Nachweis | Abschlussbefund |
|---|---|---|---|
| Konzeptionalisierung | Folien 1–3, 8 | README: Problemstellung, F1–F3, H1/H2 und Methoden | Vollständig im festgelegten Umfang |
| Lebenszyklusentwurf | Folie 4, Reserve C | README: Generation, Ingestion, Storage, Transformation, Serving und Unterströmungen | Entwurf vollständig; Serving-Dienst bleibt ausserhalb Teil 1 |
| Ingestion | Folien 3 und 5 | `ingestion.py`, Raw-CSV, Katalog- und Herkunftsmetadaten | Quelle identifiziert, Daten vorhanden, Snapshot geprüft |
| Storage | Folie 6, Reserve A | Optionenvergleich im README, `storage.py`, `schema.sql`, SQLite | Evaluiert, begründet und implementiert |
| Transformation Teil 1 | Folien 7–12, Reserve B | `transformation.py`, `analysis.py`, beide Notebooks, Qualitäts- und Ergebnisberichte | Profil, initiale Bereinigung und Hypothesentests vorhanden |
| Forschungsfragen beantworten | Folien 9–13 | Analyse-Notebook und `teil1_ergebnisse.md` | Alle drei Fragen mit Grenzen beantwortet |

## Bewertungskriterien: belastbare Nachweise

Diese Zuordnung unterstützt die Bewertung in allen fünf Bereichen, verspricht
aber keine Punktzahl. Ein Test ist beispielsweise ein Funktionalitätsnachweis
für die Implementierung, kein Ersatz für eine verständliche Konzeptbegründung.

| Kriterium | Nachweis und praktische Grenze |
|---|---|
| Kohärenz | Fragen → Datenfelder → Regeln → SQL/Statistik → Antworten; dieselbe F2-Abgrenzung in README, Notebook und Folien |
| Vollständigkeit | Zuordnung oben; Präsentation und technische Artefakte gemeinsam im Branch |
| Skalierbarkeit | Getrennte Module und explizite Pfade; nachvollziehbarer Erweiterungsweg. Keine Last- oder Server-Skalierung behauptet |
| Fachlichkeit | Quellenbruch berücksichtigt, F2 begründet eingeschränkt, Pearson-Test mit Holm und Effektgrössen |
| Funktionalität | 43 Tests, Ruff, isolierter Pipeline-/Notebook-Neulauf, SQLite-Integritätsprüfung und PowerPoint-Export |
| Objektivität | Keine unnötigen Löschungen, kein Kausalitäts-/Risikoversprechen, Grenzen und unsichere Quelldefinition offengelegt |
| Originalität | Sinnvolle eigene Projektentscheidungen: relative Zeitverteilungen, Mehrfachbeteiligung, Definitionsdiskrepanz und Jahreskontrollen |
| Signifikanz / Relevanz | Verkehrssicherheit als Motivation; konkrete Anteile und Effektstärken statt nur p-Werten |
| Eigenständigkeit | Entscheidungen und KI-Unterstützung offengelegt; das Team muss Inhalte selbst nachvollziehen und vertreten können |

## Durchgeführte Abschlussprüfung

Am 26. Oktober wurde der Stand aus Commit `f006e2d` als fachliche und technische
Grundlage geprüft; anschliessend wurden Folien, Lernhilfe und Abschlussdokumentation
ergänzt. Quelle, Bereinigungsregeln, Hypothesen und Ergebnisdaten bleiben erhalten.

- **GitHub-Abgleich:** Vor Beginn keine neueren Arbeiten auf `main` oder
  `feature/accident-data` vorhanden; keine fremden Änderungen überschrieben.
- **Automatisierte Prüfung:** `python -m pytest -q`: **43 bestanden**;
  `python -m ruff check .`: erfolgreich, einschliesslich Präsentationsgenerator.
- **Ende-zu-Ende:** Pipeline in einen separaten lokalen Prüfungsordner ausgeführt;
  beide Notebooks mit umgeleiteten Ausgabepfaden vollständig ausgeführt. Keine
  Ausgaben oder Rohdaten des Abgabebestands durch diesen Prüflauf überschrieben.
- **Reproduktion:** Bereinigte CSV, Jahres-CSV und H2-Ergebnis-CSV bytegleich;
  sämtliche fachlichen Einträge im Analyse-JSON exakt gleich. Erstellzeit und
  Datenbank-Prüfsumme des neu aufgebauten Bestands dürfen wegen Herkunftszeitstempeln
  abweichen. Die gespeicherte Abgabe-Datenbank und ihre Prüfsumme bleiben unverändert.
- **Herkunft:** Raw-, Clean- und Datenbank-SHA-256 stimmen mit den gespeicherten
  Metadaten bzw. dem Analysebericht überein. Das Analyse-Notebook prüft zusätzlich
  die SQLite-Integrität und die Verbindung der Herkunftsberichte.
- **Präsentation:** 18 Folien mit Sprechernotizen; Öffnen, PDF-Export und PNG-Rendering
  über Microsoft PowerPoint. Alle Folien visuell geprüft; ein überlanger Titel wurde
  gekürzt. Generator liest SQLite nur lesend; neue Diagramme passen zu den Ergebnissen.

Prüfumgebung wie im README: Windows, Python 3.14.3 und SQLite 3.50.4.
Beim Notebook-Prüflauf erschienen Umgebungswarnungen zu Jupyter/Windows; beide
Notebooks und Ergebnisvergleiche wurden dennoch ohne Zellfehler abgeschlossen.
Andere Betriebssysteme wurden im Abschlusscheck nicht erneut getestet.

## Inhalt des Abgabebranches

- `README.md`, Projektkonfiguration und `requirements-lock.txt`
- `src/de_projekt/` mit kommentiertem Code und SQL-Schema sowie `tests/`
- `data/raw/` mit Original-CSV und beiden Metadatendateien
- `data/processed/` mit CSV, SQLite, Qualitätsbericht und Analyseergebnissen
- `notebooks/` mit beiden ausgeführten Notebooks
- `presentations/` mit PPTX, PDF, Ergebnisgrundlage, Abbildungen und Lernhilfe
- `docs/` mit diesem Abschlussnachweis und dem historischen Review

Optionale Erzeugung der Folien nach Installation der Projektumgebung:

```powershell
python -m pip install -r presentations/requirements.txt
python presentations/build_presentation.py
# Nur unter Windows mit installiertem Microsoft PowerPoint:
powershell -NoProfile -ExecutionPolicy Bypass -File presentations/export_powerpoint.ps1
```

Der zusätzliche Foliengenerator ist keine Pipeline-Abhängigkeit. Seine
Quelldatei liegt bei, damit Inhalt und Diagramme später angepasst werden können.
PPTX und PDF sind bereits vorhanden; für ihre Nutzung muss nichts erzeugt werden.
Virtuelle Umgebungen, Caches und gerenderte Prüfvorschauen werden nicht abgegeben.
Prüfsummen der Daten und binären Präsentationsartefakte:
`docs/abgabe_sha256.json`. Text und Code werden durch den Git-Commit versioniert.

## Freeze und tatsächliche Einreichung

Der separate Branch **`abgabe/teil1`** hält den geprüften Stand fest. Er wird nach
dem Abschluss-Push nicht für Weiterentwicklung verwendet. Der zugehörige
Commit-Hash ist auf GitHub sichtbar und wird im Abschlussbericht an das Team
genannt. Ein Git-Branch ist technisch weiterhin veränderbar; es wird keine
administrative Schreibsperre behauptet. Für Teil 2 auf einem neuen Branch arbeiten.

Ein Push auf GitHub ist noch keine nachgewiesene Einreichung bei der Hochschule.
Falls das Modul einen Link, Upload oder eine Bestätigung auf einer Kursplattform
verlangt, muss das Team diesen letzten organisatorischen Schritt durchführen.
Ein entsprechender Zugang oder eine genaue Portalvorgabe wurde nicht bereitgestellt.

## Quellen und Hilfsmittel

- Daten: [Open Data Zürich, Verkehrsunfälle seit 2011](https://data.stadt-zuerich.ch/dataset/sid_dav_strassenverkehrsunfallorte),
  Datenlieferant **Bundesamt für Strassen ASTRA**. Katalogmetadaten und Lizenzstand
  sind mit dem Snapshot gespeichert.
- Datenbankwahl: [SQLite – Appropriate Uses](https://www.sqlite.org/whentouse.html).
- Testmethode: [SciPy – chi2_contingency](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html).
- Holm (1979), *A Simple Sequentially Rejective Multiple Test Procedure*,
  Scandinavian Journal of Statistics 6(2), 65–70.
- **KI-Unterstützung:** OpenAI Codex / ChatGPT unterstützte Code, Dokumentation,
  fachliche/technische Prüfung und Präsentation. Die Prüfungen wurden auf den
  vorhandenen Artefakten ausgeführt; KI-Unterstützung ersetzt keine eigene
  Erklärung oder persönliche Verantwortung des Teams. Individuelle Beiträge
  werden hier nicht erfunden. Eine eventuell kursseitig vorgeschriebene separate
  Hilfsmittelerklärung ist durch diesen Hinweis nicht automatisch ersetzt.
