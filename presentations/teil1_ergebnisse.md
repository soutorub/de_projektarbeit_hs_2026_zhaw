# Teil 1 – Ergebnisse und Präsentationsgrundlage

Quelle: Open Data Zürich; Datenlieferant: Bundesamt für Strassen ASTRA.
Datenstand: 70,767 registrierte Unfälle, 2011–2025; Raw-SHA256 `DF426E859FECD37CD7365F273662459688B1862482957960402696E8722D766F`.

## F1 – Tageszeit und Wochentag
Die Stundenverteilungen unterscheiden sich: H1 χ²(23) = 3877.06, p = numerisch 0 (Unterlauf; nicht exakt 0), Cramérs V = 0.234.
H0 wird verworfen. Häufigste Stunde: Werktage 17 Uhr, Wochenende 14 Uhr.
Nachtanteil (00–05 Uhr): Werktage 3.71 %, Wochenende 14.63 %.
Die Anteile beschreiben registrierte Unfälle innerhalb jeder Gruppe, kein individuelles Unfallrisiko.

## F2 – Beteiligung und Schwere bei Personenschadenunfällen
Primäre Analyse: 18,164 Personenschadenunfälle; Sachschäden wegen der Definitionsdiskrepanz separat gehalten.
- Fussgänger: p(Holm) = 1.444e-42, V = 0.104; H0 verworfen. Anteil schwer/tödlich: mit Beteiligung 23.42 %, ohne 15.02 %.
- Velo: p(Holm) = 7.563e-12, V = 0.054; H0 verworfen. Anteil schwer/tödlich: mit Beteiligung 18.43 %, ohne 15.25 %.
- Motorrad: p(Holm) = 6.267e-06, V = 0.036; H0 verworfen. Anteil schwer/tödlich: mit Beteiligung 19.35 %, ohne 15.97 %.
Die Anteile beziehen sich auf die Schwere des gesamten Unfalls; sie identifizieren nicht die verletzte Person und belegen keine Ursache.

## F3 – Veränderung über die Jahre
Gesamtzahl: 3,420 (2011) → 4,714 (2025); Personenschäden: 1,072 → 1,310.
Der Vergleich der Gesamtzahlen wird durch die Sachschaden-Umstellung im Juli 2015 beeinflusst. Deshalb werden Personen-/Sachschäden sowie Anteile getrennt gezeigt.
- Fussgänger-Anteil an Personenschadenunfällen: 21.27 % (2011) → 16.64 % (2025).
- Velo-Anteil an Personenschadenunfällen: 26.12 % (2011) → 40.38 % (2025).
- Motorrad-Anteil an Personenschadenunfällen: 18.84 % (2011) → 14.81 % (2025).

## Grenzen und offene Abgabeaufgaben
- Keine Verkehrsleistungsdaten: Fallzahlen und Anteile sind keine Risiken pro Fahrt oder Kilometer.
- Modellbasierte p-Werte setzen unabhängige Beobachtungen voraus; Jahreszusammensetzung und zeitliche Abhängigkeit bleiben mögliche Einflüsse.
- Beteiligungsdefinition bei Sachschäden weiterhin unklar; keine automatische Korrektur behauptet.
- Mehrfachbeteiligung: Beteiligungsanteile sind nicht gegenseitig ausschliessend.
- Die Präsentation muss Konzept und Begründungen ebenso wie diese Ergebnisse enthalten.
- Teamreview, Präsentation und eingefrorener Abgabe-Branch stehen noch aus.

## Präzisierungen aus dem fachlichen Review
Der höhere Nachtanteil am Wochenende zeigt sich in 15/15 Jahren. Die folgenden Kontrollen sind deskriptiv, keine adjustierten Tests.
- Fussgänger: höherer Anteil schwerer/tödlicher Unfälle mit Beteiligung in 15/15 Jahren.
- Velo: höherer Anteil schwerer/tödlicher Unfälle mit Beteiligung in 11/15 Jahren.
- Motorrad: höherer Anteil schwerer/tödlicher Unfälle mit Beteiligung in 13/15 Jahren.
Keine stetige Zunahme: Maximum 2018 mit 5,677 Unfällen; 2016–2025 Gesamtzahl 5,556 → 4,714, Personenschäden 1,262 → 1,310.
Details und Grenzen des Reviews des ursprünglichen Snapshots: docs/fachliches_review_teil1.md.
