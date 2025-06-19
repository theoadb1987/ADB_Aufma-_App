# ElementDesigner – Version 1 · **Variante A (Embedded Widget)**  
*Revision 2.1 · 18 Jun 2025*  

---

## 0 Was wurde korrigiert?

* Quellenangaben präzisiert (Fenstertypen, Glossar, Vorlagen, HTML‑Mock‑up).  
* Icon‑Tabelle um Belegstelle ergänzt.  
* Roadmap‑Zeiten leicht angepasst.  
* Tippfehler bereinigt.

---

## 1 Zielsetzung

Eine **eingebettete Mini‑App** innerhalb der Haupt‑Aufmaßanwendung übernimmt komplett die
Geometrie‑Berechnung und Vorschau der Fenster‑/Wand‑Schnitte.

* Läuft **im selben Prozess** (PySide6).  
* Kann als **abdockbares Fenster** (`QDockWidget` / `QDialog`) erscheinen.  
* Liefert eine **Symbol‑Bibliothek** (14 Fenstertypen) und ein **Begriffsglossar**.

---

## 2 Asset‑Setup

```
assets/
├─ schnitt/             # 34 PNG/SVG‑Schnittvorlagen   (S01_*.svg)
├─ icons/
│   ├─ fenster_types/   # 14 SVG‑Icons je Öffnungsart
│   ├─ bauteile/        # Pfosten‑, Kämpfer‑Symbole
│   └─ ui/              # Zoom‑, PDF‑, Help‑Icons
└─ glossar.json         # Tooltip‑Texte
config/
└─ schnitt_map.json     # Parameter‑→ Vorlagen‑Mapping
```

### 2.1 Fenstertyp‑Icons (14 Stk.)

| Code | Öffnungsart | Kurzbeschreibung |
|------|-------------|------------------|
| FT_F   | Festverglasung | unverriegelt |
| FT_D   | Dreh‑Fenster    | DIN L / R |
| FT_K   | Kipp‑Fenster    | oberes Kipp |
| FT_DK  | Dreh‑Kipp       | Standard |
| FT_DD  | 2‑flg. Dreh/Dreh| Mittelpfosten |
| FT_DKD | 2‑flg. Dreh‑Kipp| links + rechts |
| FT_HS  | Hebe‑Schiebe    | Parallel‑Ebene |
| FT_PSK | Parallel‑Schiebe‑Kipp | PSK |
| FT_SVG | Schwing‑Fenster | mittig gelagert |
| FT_VS  | Vertikal‑Schiebe| Double‑hung |
| FT_HS2 | Horizontal‑Schiebe | 2 Schiebeflügel |
| FT_FALT| Falt‑Fenster/Tür   | mehrteilig |
| FT_RB  | Rundbogen‑Fenster  | fest |
| FT_SCHR| Schrägelement      | fest / DK |

---

## 3 Glossar (Kurzfassung)

| Begriff | Definition |
|---------|------------|
| Sturz | Tragendes Mauerwerk über der Öffnung |
| Oberlicht | Element über dem Hauptflügel |
| Kämpfer | Horizontale Rahmen­unterteilung |
| Mittelpfosten | Vertikale Unterteilung |
| Sprosse | Profil zur Scheiben­unterteilung |
| Laibung | Wandfläche zw. Rahmen & Außenkante |

Vollständige Einträge im späteren `glossar.json`.

---

## 4 Vorlagen‑Katalog (Schnitt‑Presets)

* 34 PNG/SVG‑Schnittbilder als Basis  
* Sprossen‑Assistent & Pfosten/Kämpfer‑Offsets als Overlay‑Logik  
* Anbauteil‑Layer (Rollladen, Verbreiterung)  
* Multi‑Element‑Modus ab v2.0

---

## 5 GUI‑Referenz

Der HTML‑Prototyp zeigt:

* Akkordeon‑Sidebar für Einstellungen  
* Fenstertyp‑Grid mit Icons  
* Canvas für SVG‑Preview  
* Controls (Zoom, Export)

Wird 1:1 in PySide6 nachgebaut.

---

## 6 Roadmap

| Phase | Inhalt | Aufwand |
|-------|--------|---------|
| v1.0 | 34 Presets, 14 Icons, Glossar, Live‑Preview | 4 Tage |
| v1.1 | Sprossen‑Overlay, Pfosten/Kämpfer‑Parameter | 2 Tage |
| v2.0 | Multi‑Element, Sub‑Prozess (Var B) | 1 Woche |
| v3.0 | IFC‑Export, PDF/DXF‑Batch | 1–2 Wo |

---

## 7 To‑dos

1. SVG‑Icons nachzeichnen (0.5 T)  
2. PNG → SVG umwandeln (1 T)  
3. glossar.json füllen (0.5 T)  
4. presets.py erweitern (0.5 T)  
5. Tooltip‑Support & Icon‑Grid in UI (0.5 T)

---

*Erstellt von ChatGPT (o3) – Revision 2.1*
