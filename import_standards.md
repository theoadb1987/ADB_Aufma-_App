# Standardbibliotheken
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Sicherstellung des Projektpfads
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Drittanbieter-Bibliotheken
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QMessageBox

# Lokale Module
from models.project import Project
from services.data_service import DataService
from utils.logger import get_logger
```

## Absolute Importe

Immer absolute Importe vom Projektstamm aus verwenden:

```python
# RICHTIG
from models.project import Project
from services.data_service import DataService

# FALSCH
from ..models.project import Project
from .data_service import DataService
```

## Standardisierte Import-Statements

- Eine Klasse pro Zeile, wenn mehrere Klassen aus demselben Modul importiert werden:

```python
# RICHTIG
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import pyqtSlot

# ODER (bei wenigen Importen aus einem Modul)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot

# FALSCH
from PyQt6.QtCore import *  # Wildcard-Imports vermeiden
```

## Sicherstellung der Pfadauflösung

Folgendes am Anfang jeder Datei einfügen, um Importprobleme zu vermeiden:

```python
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
```

## Spezifische Namenskonventionen

- Logger immer über `from utils.logger import get_logger` importieren
- EventBus-Klasse und Singleton-Instanz korrekt importieren:
  ```python
  from services.event_bus import EventBus, event_bus
  ```
