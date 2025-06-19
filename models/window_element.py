from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum
import uuid

class ProfileType(Enum):
    """VEKA Profiltypen"""
    BLEND_070 = "070"
    BLEND_076_MD = "076 MD"
    BLEND_082_MD = "082 MD"
    FLUEGEL_103_229 = "103.229"
    FLUEGEL_103_232 = "103.232"
    FLUEGEL_103_380 = "103.380"
    FLUEGEL_103_381 = "103.381"

class WindowType(Enum):
    """Fenstertypen nach ElementDesigner Spezifikation"""
    FT_F = ("FT_F", "Festverglasung", "unverriegelt")
    FT_D = ("FT_D", "Dreh-Fenster", "DIN L / R")
    FT_K = ("FT_K", "Kipp-Fenster", "oberes Kipp")
    FT_DK = ("FT_DK", "Dreh-Kipp", "Standard")
    FT_DD = ("FT_DD", "2-flg. Dreh/Dreh", "Mittelpfosten")
    FT_DKD = ("FT_DKD", "2-flg. Dreh-Kipp", "links + rechts")
    FT_HS = ("FT_HS", "Hebe-Schiebe", "Parallel-Ebene")
    FT_PSK = ("FT_PSK", "Parallel-Schiebe-Kipp", "PSK")
    FT_SVG = ("FT_SVG", "Schwing-Fenster", "mittig gelagert")
    FT_VS = ("FT_VS", "Vertikal-Schiebe", "Double-hung")
    FT_HS2 = ("FT_HS2", "Horizontal-Schiebe", "2 Schiebeflügel")
    FT_FALT = ("FT_FALT", "Falt-Fenster/Tür", "mehrteilig")
    FT_RB = ("FT_RB", "Rundbogen-Fenster", "fest")
    FT_SCHR = ("FT_SCHR", "Schrägelement", "fest / DK")
    
    def __init__(self, code, display_name, description):
        self.code = code
        self.display_name = display_name
        self.description = description

@dataclass
class WindowElement:
    """Datenmodell für ein Fensterelement"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    x: float = 0.0
    y: float = 0.0
    width: float = 1000.0
    height: float = 1200.0
    profile_type: ProfileType = ProfileType.BLEND_070
    window_type: WindowType = WindowType.FT_DK
    comment: str = ""
    rotation: float = 0.0
    is_selected: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Berechnete Profilmaße
    profile_width_a: float = 0.0
    profile_width_b: float = 0.0
    profile_width_c: float = 0.0
    profile_width_d: float = 0.0
    
    @property
    def center_x(self) -> float:
        return self.x + self.width / 2
    
    @property
    def center_y(self) -> float:
        return self.y + self.height / 2
    
    def get_bounds(self) -> tuple[float, float, float, float]:
        """Gibt (x, y, x+width, y+height) zurück"""
        return (self.x, self.y, self.x + self.width, self.y + self.height)