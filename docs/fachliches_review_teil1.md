# Fachliches Review – Teil 1

Stand: 13. Oktober 2026. Grundlage: Aufgabenfolie, README, Code, SQL-Schema,
Raw-/Processed-Artefakte und beide ausgeführten Notebooks.

**Historisches Review vom 13. Oktober:** Die damaligen offenen organisatorischen
Schritte sind unten im damaligen Stand beschrieben. Den aktuellen Abschlussstand
mit Präsentation und erneutem Prüflauf dokumentiert [abgabe_teil1.md](abgabe_teil1.md).

## Urteil und Reichweite

Die Lösung passt zum Teil-1-Umfang: eine begründete lokale Batch-Pipeline,
reproduzierbare Datengrundlage, relationaler Speicher, initiale Bereinigung und
deskriptive Analyse mit Hypothesentests. Machine Learning und ein eigener
Serving-Dienst sind dafür nicht erforderlich. Präsentation, gemeinsames
Verständnis der Entscheidungen und eingefrorener Abgabe-Branch stehen noch aus.
Das Review bestätigt keine Note und ersetzt nicht die Prüfung durch das Team.

## Nachrechnung der Ergebnisse

Die Tabellen wurden erneut lesend aus SQLite gebildet. Unabhängig von
`analysis.independence_test()` wurden erwartete Häufigkeiten als
`Zeilensumme × Spaltensumme / Gesamtzahl`, Pearson-Statistik als
`Summe((beobachtet-erwartet)²/erwartet)` und Cramérs V daraus berechnet.
Die p-Werte wurden mit der Chi-Quadrat-Verteilung bestimmt. Die Holm-Korrektur
wurde getrennt durch Sortieren, Multiplikation mit der Zahl verbleibender Tests
und kumulatives Maximum geprüft. Die gespeicherten Ergebnisse stimmen überein.

| Test | Fallzahl | χ² | Cramérs V | Ergebnis |
|---|---:|---:|---:|---|
| H1 | 70'767 | 3'877,063 | 0,234065 | H0 unter dem verwendeten Modell verworfen; p numerisch unterlaufen |
| H2 Fussgänger | 18'164 | 194,879 | 0,103580 | Nach Holm signifikant |
| H2 Velo | 18'164 | 52,602 | 0,053814 | Nach Holm signifikant |
| H2 Motorrad | 18'164 | 23,961 | 0,036320 | Nach Holm signifikant |

Die kleinsten erwarteten Zellen liegen über 5. Dies stützt die asymptotische
Berechnung, beweist aber nicht die Unabhängigkeit der Beobachtungen.
Methodenquelle: [SciPy chi2_contingency](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html).

## Bewertung nach Inhalt

| Bereich | Fachlich passend | Einschränkung / Konsequenz |
|---|---|---|
| Konzept | Fragen sind mit Feldern und Methoden verbunden; F2 ausdrücklich auf Personenschäden begrenzt | Erkenntnisziel ist Beschreibung registrierter Unfälle, keine individuelle Risikoprognose |
| Lebenszyklus | Generation und externe Datenerfassung getrennt von eigener Pipeline; Storage begleitet mehrere Phasen | Der Entwurf kann erweitert werden; tatsächliche Last-/Mehrnutzer-Skalierung wurde nicht getestet |
| Ingestion | Unveränderter Snapshot, Herkunftsmetadaten, Integritätsprüfung und bewusste Updates | CSV-Formatprüfung beweist keine inhaltliche Vollständigkeit; Quelleninterpretation bleibt nötig |
| Storage | SQLite ist für einen lokalen, überwiegend lesenden Bestand angemessen; Primärschlüssel und Constraints verhindern ungültige Speicherung | Portabilität bezieht sich auf die DB-Datei; die gesamte Referenzumgebung wurde nur unter Windows/Python 3.14 geprüft |
| Bereinigung | Keine unbegründete Zeilenlöschung oder Imputation; explizite Typen und fehlende Angaben; dreistufige boolesche Logik | Eine nicht leere unbekannte Kategorie löst einen Fehler aus und muss fachlich beurteilt werden; sie wird nicht automatisch repariert |
| Hypothesentests | Passende Kreuztabellen, Mehrfachbeteiligung korrekt getrennt, Holm und Effektgrössen | Gepoolte Assoziation ist nicht um Jahr, Exposition oder andere Beteiligungen bereinigt |

## Präzisierungen für Interpretation und Präsentation

### 1. Statistische Signifikanz ist keine Unfallursache

Wir haben einen Bestand registrierter Unfälle, keine Zufallsstichprobe aller
Verkehrsteilnehmenden. Die p-Werte beziehen sich auf das verwendete
Unabhängigkeitsmodell. Wiederkehrende Orte, zeitliche Abhängigkeiten, Infrastruktur,
Verkehrsaufkommen und weitere Merkmale können dieses Modell begrenzen.
Die beobachteten Anteile und Effektgrössen beschreiben den Bestand unabhängig davon.
Weder «Beteiligung verursacht schwere Unfälle» noch «Velofahren ist gefährlicher»
ist aus dieser Analyse ableitbar.

### 2. Jahreskontrollen nicht als adjustierte Tests ausgeben

Aus den vorhandenen Jahresdaten nachgerechnet:

- Der Nachtanteil ist am Wochenende in **15 von 15 Jahren** höher als werktags.
- Der Anteil schwerer/tödlicher Personenschadenunfälle ist mit Fussgängerbeteiligung
  in **15 von 15 Jahren** höher als ohne dieses Merkmal.
- Bei Velobeteiligung gilt die höhere Quote in **11 von 15 Jahren**, bei
  Motorradbeteiligung in **13 von 15 Jahren**.

Das sind deskriptive Richtungskontrollen, keine 45 zusätzlichen Signifikanztests.
Die letzten beiden Zusammenhänge dürfen nicht als in jedem Jahr gleichgerichtet
oder gleich stark dargestellt werden. Das primäre H2-Ergebnis bleibt ein gepoolter
Zusammenhang über 2011–2025 und umfasst drei Schweregrade; diese Kontrolle fasst
Schwerverletzte/Getötete nur zur Interpretation zusammen.

### 3. F3 beschreibt keine stetige Zunahme

2011 und 2025 allein zeigen nicht den Verlauf. Der höchste Gesamtbestand liegt
2018 bei 5'677 Unfällen, 2025 sind es 4'714. Nach dem Umstellungsjahr zeigt der
Vergleich 2016–2025: Gesamtzahl 5'556 → 4'714, Sachschäden 4'294 → 3'404,
Personenschäden 1'262 → 1'310. Die Reihen entwickeln sich also unterschiedlich.
Der Abschnitt nach 2015 vermeidet den bekannten Meldebruch zwischen den
Vergleichsjahren, garantiert aber nicht die Abwesenheit anderer Erfassungsänderungen.
Alle Jahreswerte und Schwereanteile werden im Notebook gezeigt.

### 4. Die Dokumentationsdiskrepanz ist offen

Die offizielle [Quellenbeschreibung](https://data.stadt-zuerich.ch/dataset/sid_dav_strassenverkehrsunfallorte)
nennt Personenschäden in den Beteiligungsdefinitionen. Positive Beteiligung bei
Sachschäden im Snapshot widerspricht dieser engen Lesart. Wir behaupten weder
einen nachgewiesenen Datenfehler noch eine geklärte neue Definition. Die Abgrenzung
von F2/H2 auf Personenschäden ist eine vorsichtige Projektentscheidung.

### 5. Eine Zeile und ein Schweregrad gehören zum Unfall

Legenden müssen «Unfälle mit Getöteten/Schwerverletzten/Leichtverletzten» sagen,
damit die Diagramme nicht als Personenzahlen gelesen werden. Die Beteiligung
identifiziert nicht, wer verletzt wurde. Die Schwere bezieht sich auf den gesamten Unfall.

### 6. Features nach tatsächlichem Nutzen einordnen

`is_weekend` wird in H1 genutzt. `time_period` ist eine verständliche Zusatzgruppierung;
der primäre H1-Test nutzt die Originalstunde. `vulnerable_road_user` ist ein
ergänzendes, korrekt abgeleitetes Merkmal und kein eigener Faktor der aktuellen
Hypothesentests. Für Teil 1 keine zusätzlichen Analysen allein zur Nutzung dieses
Features bauen; es darf nicht als Beleg einer bereits beantworteten Zusatzfrage gelten.

## Schlussstand

Rechenweg und Datenstruktur sind fachlich nachvollziehbar. Die beschriebenen
Präzisierungen werden im README und der Ergebnisgrundlage berücksichtigt; die
Legenden werden im Analyse-Notebook korrigiert. Offene Modell- und Quellengrenzen
werden nicht durch weitere technische Komplexität verdeckt.
Vor der Abgabe muss das Team erklären können, was ein Unfallzählwert, Anteil,
p-Wert und Effektgrösse jeweils bedeutet. Danach folgt die Präsentation.
