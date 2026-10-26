# Vorbereitung auf die Präsentation – Teil 1

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

### Folie 1: Worum geht es? (ca. 35 Sekunden)

Wir untersuchen polizeilich registrierte Verkehrsunfälle in der Stadt Zürich. Unser Ziel ist einerseits eine nachvollziehbare Data-Engineering-Pipeline und andererseits die Beantwortung von drei Forschungsfragen. Dafür verwenden wir 70’767 Unfälle von 2011 bis 2025. Wir beschreiben diesen registrierten Bestand. Eine Prognose oder ein individuelles Unfallrisiko berechnen wir in Teil 1 nicht.

**Merken:** Eine Zeile ist ein Unfall, nicht eine verletzte Person oder eine Fahrt.

### Folie 2: Problemstellung und Forschungsfragen (ca. 55 Sekunden)

Unsere drei Fragen bestimmen die Umsetzung. Erstens: Wie unterscheiden sich Unfälle nach Tageszeit und Wochentag? Zweitens: Gibt es bei Personenschadenunfällen einen Zusammenhang zwischen Beteiligung und Schwere? Drittens: Wie verändern sich Anzahl und Zusammensetzung über die Jahre? Für die ersten beiden Fragen nutzen wir Hypothesentests, für die dritte eine deskriptive Zeitreihe. Der Engineering-Beitrag ist die kontrollierte Kette von der Quelle bis zum Ergebnis. So lassen sich unsere Zahlen auf einen bestimmten Datenstand und klare Regeln zurückführen.

**Merken:** Jede technische Komponente muss eine dieser Fragen oder die Reproduzierbarkeit unterstützen.

### Folie 3: Quelle und Aussagegrenzen (ca. 60 Sekunden)

Die Quelle stammt aus dem Open-Data-Katalog der Stadt Zürich, Datenlieferant ist das ASTRA. Der Rohbestand enthält 36 Spalten. Wichtig sind zwei fachliche Befunde. Ab Juli 2015 wurden auch Bagatellunfälle gemeldet; ein Sprung der Gesamtzahl kann deshalb durch die Erfassung entstehen. Ausserdem beschreibt der Katalog die Beteiligungsfelder mit Bezug auf Personenschäden, während auch Sachschadenzeilen positive Werte besitzen. Die Ursache haben wir nicht geklärt. Wir erhalten die Werte und beschränken F2 vorsichtig auf Personenschadenunfälle. Das ist eine begründete Abgrenzung und keine behauptete Reparatur der Quelle.

**Merken:** Nicht registrierte Unfälle fehlen. Auffällige Daten sind nicht automatisch bewiesene Fehler.

### Folie 4: Data-Engineering-Lebenszyklus (ca. 65 Sekunden)

Die Daten entstehen durch die polizeiliche Erfassung und das ASTRA-System. Wir übernehmen die veröffentlichten Daten als kontrollierten Snapshot. Raw-Dateien bleiben erhalten; die Transformation erzeugt eine bereinigte CSV, die wir in SQLite speichern. Die Analyse liest aus SQLite und erzeugt Ergebnisse. Die Grafik zeigt die Verantwortungen der Phasen, nicht eine starre zeitliche Reihenfolge: Speicherung findet mehrfach statt. Quer dazu laufen unter anderem Datenqualität, Sicherheit und Nachvollziehbarkeit. Die Pipeline orchestriert die Schritte und stoppt bei Fehlern. Serving bedeutet hier SQL, Notebooks und Ergebnisartefakte; ein eigener Dienst bleibt ausserhalb von Teil 1.

**Merken:** Unser tatsächlicher Datenfluss: Download → Raw → Transformation → CSV → SQLite → Analyse.

### Folie 5: Ingestion und Snapshot (ca. 45 Sekunden)

Die Ingestion beschafft die CSV und hält ihren Ursprung fest. Ein Snapshot ist eine gespeicherte Version der Quelle. Die Prüfsumme ist wie ein digitaler Fingerabdruck: Ändern sich Bytes, passt sie nicht mehr. Dadurch vermeiden wir, dass unterschiedliche Gruppenmitglieder unbemerkt verschiedene Datenstände analysieren. Der Standardlauf nutzt den vorhandenen Snapshot offline. Ein bewusster Refresh legt einen neuen Datenstand separat ab. Eine gültige Prüfsumme beweist allerdings nur Integrität, nicht, dass jede Unfallmeldung inhaltlich stimmt.

**Merken:** Raw wird erhalten; bei einem Fehler wird nicht still ein neuer Datenstand heruntergeladen.

### Folie 6: Warum SQLite? (ca. 60 Sekunden)

Wir haben CSV, SQLite und PostgreSQL verglichen. CSV bewahrt das Originalformat, bietet aber keine Datenbank-Constraints. SQLite erlaubt SQL, eindeutige Schlüssel und geprüfte Wertebereiche in einer einzigen Datei. Für 70’767 Zeilen mit einem kontrollierten Ladeprozess und anschliessenden Leseanalysen reicht das aus. PostgreSQL wäre eine Option bei einer zentralen Datenbank mit vielen parallelen Schreibzugriffen. Diese Anforderung haben wir nicht. Jedes Teammitglied nutzt eine lokale Kopie; wir bearbeiten nicht gleichzeitig eine geteilte SQLite-Datei. Die relationale Struktur passt, weil jede Zeile einen Unfall mit fester ID und vergleichbaren Merkmalen beschreibt.

**Merken:** SQLite ist eine Datenbank, keine Excel-Datei. Auswahl nach Bedarf begründen, nicht nach Prestige.

### Folie 7: Datenprofil, Bereinigung und Features (ca. 60 Sekunden)

Das Datenprofil untersucht zunächst Qualität und Wertebereiche. Im aktuellen Snapshot fehlen keine Felder und es gibt keine doppelten Unfall-IDs. Deshalb löschen wir keine Zeilen und erfinden keine fehlenden Werte. Wir wählen 19 Originalfelder, setzen Datentypen und ergänzen drei Merkmale. is_weekend fasst Samstag und Sonntag zusammen; time_period bildet vier Sechs-Stunden-Blöcke. vulnerable_road_user verknüpft Fussgänger- oder Velobeteiligung. Das letzte Merkmal ist eine ergänzende Gruppierung und kein eigener Test im aktuellen Ergebnis. Die Rohdaten enthalten weiterhin alle Originalspalten. Ein Qualitätsbericht dokumentiert Auswahl, Regeln und unveränderte Fallzahl.

**Merken:** Bereinigung kann Typisierung und Validierung bedeuten. 0 bedeutet nein, NULL bedeutet unbekannt.

### Folie 8: Hypothesen und Testlogik (ca. 65 Sekunden)

Der Chi-Quadrat-Test vergleicht beobachtete Häufigkeiten mit den Häufigkeiten, die unter der Nullhypothese zu erwarten wären. Bei H1 sind das zwei Gruppen und 24 Stunden. Bei H2 prüfen wir je Beteiligungsmerkmal zwei Gruppen und drei Schweregrade: leicht, schwer und tödlich. Ein Unfall zählt pro Test genau einmal, darf aber mehrere Beteiligungsmerkmale haben. Weil wir bei H2 drei Tests durchführen, verwenden wir Holm zur Korrektur der p-Werte. Der p-Wert beschreibt die Vereinbarkeit mit dem Modell; Cramérs V die Stärke der beobachteten Assoziation. Alle erwarteten Zellen sind ausreichend gross, aber zeitliche Abhängigkeiten können die Modellinterpretation begrenzen.

**Merken:** p < 0,05 beweist weder eine Ursache noch eine grosse praktische Bedeutung.

### Folie 9: F1: Tageszeit und Wochentag (ca. 65 Sekunden)

Die Kurven summieren sich innerhalb der jeweiligen Gruppe auf 100 Prozent. Damit vergleichen wir die Form der Stundenverteilung und nicht einfach fünf Werktage mit zwei Wochenendtagen. Werktags liegt die häufigste Stunde bei 17 Uhr, am Wochenende bei 14 Uhr. Zwischen Mitternacht und fünf Uhr liegen 3,71 Prozent der Werktagsunfälle und 14,63 Prozent der Wochenendunfälle. Der Unterschied ist im verwendeten Test signifikant; Cramérs V beträgt 0,234. Das Muster eines höheren Nachtanteils am Wochenende sehen wir deskriptiv in allen 15 Jahren. Wir wissen damit aber nicht, wie hoch das Risiko einer einzelnen Fahrt ist, weil uns die Zahl und Länge der Fahrten fehlen.

**Merken:** Die Nenner sind alle Werktagsunfälle beziehungsweise alle Wochenendunfälle.

### Folie 10: F2: Beteiligung und Unfallschwere (ca. 65 Sekunden)

Für diese Frage betrachten wir 18’164 Personenschadenunfälle. Die Balken zeigen zur Interpretation den Anteil schwerer oder tödlicher Unfälle. Mit Fussgängerbeteiligung sind es 23,42 Prozent, ohne 15,02 Prozent. Auch bei Velo und Motorrad liegen die dargestellten Anteile mit Beteiligung höher. Die eigentlichen Tests verwenden alle drei Schweregrade getrennt. Alle drei Ergebnisse sind nach Holm signifikant, die Effektgrössen sind aber numerisch klein. Ein Unfall kann mehrere Beteiligungsmerkmale besitzen. Die Schwere gehört zum gesamten Unfall; wir können nicht daraus ableiten, wer verletzt wurde oder dass eine bestimmte Beteiligung den Schaden verursacht.

**Merken:** F2 beschreibt Unfälle, nicht die Gefährlichkeit einer Verkehrsart pro Kilometer.

### Folie 11: F3: Zeitliche Veränderung (ca. 65 Sekunden)

Links stehen die jährlichen Fallzahlen. Die gestrichelte Linie markiert den bekannten Erfassungswechsel 2015. Der Höchststand liegt 2018, daher wäre die Aussage einer stetigen Zunahme falsch. Zwischen 2016 und 2025 sinken die Gesamtzahlen von 5’556 auf 4’714; Personenschadenunfälle steigen im selben Vergleich leicht von 1’262 auf 1’310. Rechts sehen wir die Beteiligungsanteile innerhalb der Personenschadenunfälle. Der Veloanteil steigt von 26,12 Prozent im Jahr 2011 auf 40,38 Prozent im Jahr 2025. Das ist eine Veränderung der Zusammensetzung. Ohne Verkehrsleistung können wir daraus keine Veränderung des Risikos beim Velofahren ableiten. Die Beteiligungsanteile sind wegen Mehrfachbeteiligung nicht additiv.

**Merken:** Personenschadenunfälle sind Unfallzahlen, keine Zahl verletzter Personen.

### Folie 12: Funktionalität und fachliche Grenzen (ca. 45 Sekunden)

Die technische Prüfung umfasst 43 automatisierte Tests, die Codeprüfung, die Pipeline und beide Notebooks. Ein isolierter Neulauf erzeugt dieselben fachlichen Ergebnisse. Die Datenbank wird vor dem Austausch geprüft. Das zeigt, dass unser Verfahren funktioniert. Es beweist aber nicht, dass die Quelldaten alle tatsächlichen Unfälle enthalten oder dass unsere Zusammenhänge kausal sind. Es fehlen Verkehrsleistung und weitere Einflussgrössen. Daher bleiben die Aussagen auf den registrierten Bestand und das verwendete Modell begrenzt.

**Merken:** Tests prüfen Programmverhalten; sie sind keine Garantie für vollständige oder wahre Quelldaten.

### Folie 13: Kernaussagen zusammenführen (ca. 40 Sekunden)

Zusammenfassend unterscheiden sich die zeitlichen Muster zwischen Werktagen und Wochenenden. Beteiligung und Schwere stehen bei Personenschadenunfällen in einem statistischen Zusammenhang, dessen Stärke wir einordnen müssen. Die jährliche Entwicklung ist nicht einheitlich; besonders der Erfassungswechsel verhindert einfache Schlussfolgerungen aus Gesamtzahlen. Die Pipeline schafft dafür eine überprüfbare Grundlage von der Quelle bis zur Antwort. Das ist unser Ergebnis von Teil 1.

**Merken:** Die fachliche Aussage und die technische Grundlage gehören zusammen.

### Folie 14: Abschluss und Nachweise (ca. 25 Sekunden)

Die Abgabe enthält die Präsentation sowie den Code, die Originaldaten, den bereinigten Bestand, die Datenbank und die ausgeführten Analysen. Das README erklärt den Einstieg. Der separate Abgabebranch hält den geprüften Stand für Teil 1 fest. Erweiterungen für Teil 2 erfolgen getrennt davon. Vielen Dank, wir beantworten gerne Fragen.

**Merken:** Ein eingefrorener Branch ist eine Arbeitsvereinbarung; der genaue Commit identifiziert den Stand.

### Folie 15: Reserve: Datenmodell und SQL (nur bei Rückfragen)

Eine Tabelle reicht, weil unsere Beobachtungseinheit der Unfall ist und wir keine eigenen Personen- oder Fahrzeugdatensätze besitzen. Der Primärschlüssel verhindert doppelte IDs. CHECK-Regeln prüfen Wertebereiche und die Konsistenz berechneter Features. pipeline_metadata dokumentiert die Herkunft. Das SQL-Beispiel zählt Personenschadenunfälle pro Jahr. Die Tabelle ist relational nutzbar, auch ohne mehrere Dimensionstabellen.

**Merken:** Die Datei accidents.sqlite reicht zum Öffnen; Code und Rohdaten sind für Reproduktion nötig.

### Folie 16: Reserve: Zahlen und Testannahmen (nur bei Rückfragen)

Der H1-p-Wert wird als kleiner als 0,001 berichtet, weil die Gleitkommaberechnung auf null unterläuft. Er ist nicht mathematisch null. Bei H2 zeigt die Tabelle die Holm-korrigierten Werte. Cramérs V lässt die Grössenordnung der Assoziation erkennen. Alle erwarteten Häufigkeiten liegen über fünf. Dies stützt die asymptotische Berechnung, beweist aber nicht die zeitliche Unabhängigkeit oder Kausalität.

**Merken:** df sind Freiheitsgrade; für eine R×C-Tabelle gilt (R−1)×(C−1).

### Folie 17: Reserve: Unterströmungen und Skalierung (nur bei Rückfragen)

Nachvollziehbarkeit entsteht durch dokumentierte Herkunft, Regeln und Versionen. Fehler stoppen die Verarbeitung. Die lokale Batch-Pipeline passt zur jährlich veröffentlichten Quelle. Für erheblich grössere Daten könnten wir chunkweise arbeiten; für eine zentrale Datenbank mit vielen Schreibzugriffen wäre PostgreSQL neu zu evaluieren. Diese Möglichkeiten sind ein Entwurf, keine nachgewiesene Lastskalierung. Die öffentliche Quelle wird nicht zur Identifizierung beteiligter Personen verknüpft.

**Merken:** Eine geplante Erweiterung nicht als bereits implementierte Funktion darstellen.

### Folie 18: Reserve: Quellen und Hilfsmittel (nur bei Rückfragen)

Die Datenquelle wird mit ASTRA als Datenlieferant angegeben. SQLite und SciPy sind durch offizielle Dokumentation belegt. Die Holm-Korrektur folgt der Veröffentlichung von 1979. KI-Unterstützung ist offengelegt: Sie wurde für Implementierung, Dokumentation, Prüfung und Präsentation verwendet. Eine kursspezifische Erklärung ist gegebenenfalls zusätzlich nach dessen Vorgaben einzureichen; solche Vorgaben liegen uns nicht vor.

**Merken:** Nur persönlich geprüfte und verstandene Arbeit als eigene Erklärung vertreten.

## Typische Fragen mit kurzen Antworten

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
