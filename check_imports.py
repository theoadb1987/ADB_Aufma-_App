"""
Dieses Skript durchsucht alle Python-Dateien im Projekt nach fehlerhaften Importen.
"""
import os
import re
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def check_imports(directory='.'):
    """Durchsucht alle Python-Dateien im angegebenen Verzeichnis nach problematischen Importen."""
    problematic_imports = []
    
    # Muster für die zu prüfenden Importe
    patterns = [
        {
            "name": "Logger-Import falsch",
            "regex": re.compile(r'from\s+logger\s+import|import\s+logger\b'),
            "correct": "from utils.logger import get_logger"
        },
        {
            "name": "EventBus-Import falsch",
            "regex": re.compile(r'from\s+event_bus\s+import|import\s+event_bus\b'),
            "correct": "from services.event_bus import EventBus, event_bus"
        },
        {
            "name": "Wildcard-Import",
            "regex": re.compile(r'from\s+[\w\.]+\s+import\s+\*'),
            "correct": "Spezifische Klassen/Funktionen importieren statt *"
        },
        {
            "name": "Relativer Import",
            "regex": re.compile(r'from\s+\.\.?\w*\s+import'),
            "correct": "Absolute Importe vom Projektstamm verwenden"
        }
    ]
    
    # Rekursiv durch alle Dateien gehen
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        line_number = 1
                        lines = content.split('\n')
                        
                        # Auf problematische Importe prüfen (zeilenweise)
                        for line in lines:
                            for pattern in patterns:
                                if pattern["regex"].search(line):
                                    problematic_imports.append({
                                        "file": file_path,
                                        "line": line_number,
                                        "content": line.strip(),
                                        "issue": pattern["name"],
                                        "correct": pattern["correct"]
                                    })
                            line_number += 1
                            
                        # Prüfen, ob die Pfad-Auflösung fehlt
                        has_path_resolution = False
                        for i in range(min(20, len(lines))):  # Erste 20 Zeilen prüfen
                            if "project_root" in lines[i] and "sys.path" in lines[i]:
                                has_path_resolution = True
                                break
                                
                        if not has_path_resolution and not file_path.endswith('__init__.py'):
                            problematic_imports.append({
                                "file": file_path,
                                "line": 1,
                                "content": "# Keine Pfad-Auflösung gefunden",
                                "issue": "Fehlende Pfad-Auflösung",
                                "correct": "import sys, os; project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, project_root)"
                            })
                            
                except Exception as e:
                    print(f"Fehler beim Lesen von {file_path}: {e}")
    
    return problematic_imports

def print_report(issues):
    """Gibt einen formatierten Bericht der gefundenen Probleme aus."""
    if not issues:
        print("✅ Keine problematischen Importe gefunden!")
        return
        
    print(f"\n🔍 {len(issues)} problematische Importe gefunden:")
    print("-" * 80)
    
    # Nach Dateien gruppieren
    files = {}
    for issue in issues:
        if issue["file"] not in files:
            files[issue["file"]] = []
        files[issue["file"]].append(issue)
    
    # Für jede Datei die Probleme ausgeben
    for file_path, file_issues in files.items():
        print(f"\n📄 {file_path}")
        for issue in file_issues:
            print(f"  Zeile {issue['line']}: {issue['issue']}")
            print(f"    ❌ {issue['content']}")
            print(f"    ✅ {issue['correct']}")
    
    print("\n" + "-" * 80)
    print(f"Insgesamt {len(issues)} Probleme in {len(files)} Dateien gefunden.")

def main():
    """Hauptfunktion für den Skriptaufruf."""
    directory = '.' if len(sys.argv) < 2 else sys.argv[1]
    issues = check_imports(directory)
    print_report(issues)

if __name__ == "__main__":
    main()
