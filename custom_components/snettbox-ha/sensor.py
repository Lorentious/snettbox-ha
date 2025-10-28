#mit DataUpdateCoordinator
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from datetime import timedelta
from .const import DOMAIN
import logging
import json
import os

_LOGGER = logging.getLogger(__name__)

# Icons laden
ICON_PATH = os.path.join(os.path.dirname(__file__), "icons.json")
try:
    with open(ICON_PATH, "r", encoding="utf-8") as f:
        ICON_MAP = json.load(f)
except Exception as e:
    _LOGGER.warning(f"Konnte icons.json nicht laden: {e}")
    ICON_MAP = {}

def flatten_keys(d, parent_key=""):
    """Rekursiv alle Keys aus dict holen, mit Punkt-Notation"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}.{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_keys(v, new_key))
        else:
            items.append(new_key)
    return items

def get_value_from_path(data, path):
    """Hole Wert anhand Pfad mit Punkt-Notation"""
    for part in path.split("."):
        if isinstance(data, dict) and part in data:
            data = data[part]
        else:
            return None
    return data


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup Sensors using DataUpdateCoordinator"""
    ip = entry.data["IP-Address"]
    name = entry.data["Name"]
    update_interval = entry.data.get("Interval", 15)
    selected_groups = entry.data["selected_groups"]

    session = async_get_clientsession(hass)
    url = f"http://{ip}/"

    # Coordinator für die JSON-Abfrage
    async def async_update_data():
        try:
            async with session.get(url, timeout=5, ssl=False) as resp:
                data = await resp.json()
            return data.get("SBI", {})
        except Exception as e:
            _LOGGER.error(f"Fehler beim Abrufen der JSON-Daten: {e}")
            return {}

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{name} SBI Coordinator",
        update_method=async_update_data,
        update_interval=timedelta(seconds=update_interval),
    )

    await coordinator.async_config_entry_first_refresh()

    uid = coordinator.data.get("UID", "unknown")
    version = coordinator.data.get("Ver", "unknown")

    entities = []

    # UID und Ver als eigene Sensoren
    entities.append(SnettboxCoordinatorSensor(coordinator, name, "Device", "UID", ip, uid, version))
    entities.append(SnettboxCoordinatorSensor(coordinator, name, "Device", "Ver", ip, uid, version))

    # Ausgewählte Keys
    for key in selected_groups:
        if key in ("UID", "Ver"):
            continue
        group = key.split(".")[0]
        entities.append(SnettboxCoordinatorSensor(coordinator, name, group, key, ip, uid, version))

    # Sortieren nach Gruppe und Key
    entities.sort(key=lambda e: (e._group, e._key))

    async_add_entities(entities, True)


class SnettboxCoordinatorSensor(CoordinatorEntity, Entity):
    """Sensor, der Werte aus dem Coordinator bezieht"""

    def __init__(self, coordinator, base_name, group, key, ip, uid, version):
        super().__init__(coordinator)
        self._base_name = base_name
        self._group = group
        self._key = key
        self._ip = ip
        self._uid = uid
        self._version = version

        # Friendly Name: Gruppe:Schlüssel
        #key_short = key[len(group)+1:] if key.startswith(group + ".") else key
        #self._name = f"{group}:{key_short}"
        #ersetzt durch:
        key_short = self._key[len(self._group)+1:] if self._key.startswith(self._group + ".") else self._key
        # Friendly Name: Gruppe:Schlüssel, nur Schlüssel wenn gleich
        self._name = key_short if key_short == self._group else f"{self._group}:{key_short}"


    @property
    def name(self):
        return self._name

    @property
    def state(self):
        value = get_value_from_path(self.coordinator.data, self._key)
        return value if value is not None else "unbekannt"

    @property
    def unique_id(self):
        return f"{self._ip}_{self._group}_{self._key}"

    @property
    def should_poll(self):
        return False

    @property
    def icon(self):
        return ICON_MAP.get(self._key)

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._uid)},
            "name": self._base_name,
            "manufacturer": "battery-direct",
            "model": "Snettbox",
            "sw_version": self._version,
            "model_id": self._uid,
        }
