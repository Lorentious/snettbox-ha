# Snettbox-HA
Home Assistant Integration für die **Snettbox** – mit automatischer Entitätserzeugung und **Config Flow**.


## 🔍 Beschreibung
`snettbox-ha` liest die Daten der Snettbox über deren JSON-Schnittstelle aus und stellt sie in Home Assistant als Sensoren strukturiert zur Verfügung.  
Die Integration wird über den Home-Assistant Konfigurationsdialog eingerichtet – **ohne YAML**.


## 🎯 Features
- Einrichtung direkt über **UI / Config Flow**
- Automatische Entitätenerzeugung
- Gruppierung von Sensoren (z. B. `GRID`, `SB`, …)
- Einstellbares Update-Intervall
- HACS-kompatibel als **Custom Repository**


## 🧩 Voraussetzungen
- Home Assistant
- Die Snettbox muss über das Netzwerk erreichbar sein (lokale IP)
- JSON-Endpoint der Snettbox muss erreichbar sein (Browser-Test empfohlen)


## ⚙️ Installation über HACS (Custom Repository)

1. **HACS** öffnen → *Integrationen*
2. Rechts oben **⋯** → *Custom repositories*
3. Folgende URL eintragen:
https://github.com/Lorentious/snettbox-ha

4. Kategorie: **Integration**
5. Repository hinzufügen
6. Danach in HACS → *Integrationen installieren*
7. Home Assistant **neu starten**


## 🧠 Einrichtung (Config Flow)

1. **Einstellungen → Geräte & Dienste**
2. **Integration hinzufügen**
3. **Snettbox HA** auswählen
4. IP-Adresse der Snettbox und optional Update-Intervall eingeben
5. Fertig ✅

> Keine `configuration.yaml` notwendig.


## 📊 Nutzung
Nach der Einrichtung werden automatisch Sensor-Entitäten angelegt.

Diese Sensoren können direkt in **Dashboards**, Automationen, Statistiken oder Grafiken verwendet werden.


## 🤝 Entwicklung
Das Projekt wurde gemeinsam (Vater + Sohn) entwickelt für [Snettbox](https://www.snettbox.de/) – Verbesserungen und Ideen sind willkommen!  
Pull-Requests & Issues gerne über GitHub.

## 📄 Lizenz

This project is licensed under the MIT License.
