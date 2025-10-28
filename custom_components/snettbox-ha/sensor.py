# from homeassistant.helpers.entity import Entity
# from homeassistant.helpers.aiohttp_client import async_get_clientsession
# from homeassistant.helpers.event import async_track_time_interval
# from datetime import timedelta
# from .const import DOMAIN
# import logging
# import json
# import os

# _LOGGER = logging.getLogger(__name__)

# # Icons laden
# ICON_PATH = os.path.join(os.path.dirname(__file__), "icons.json")
# try:
#     with open(ICON_PATH, "r", encoding="utf-8") as f:
#         ICON_MAP = json.load(f)
# except Exception as e:
#     _LOGGER.warning(f"Konnte icons.json nicht laden: {e}")
#     ICON_MAP = {}

# def flatten_keys(d, parent_key=""):
#     """Rekursiv alle Keys aus dict holen, mit Punkt-Notation"""
#     items = []
#     for k, v in d.items():
#         new_key = f"{parent_key}.{k}" if parent_key else k
#         if isinstance(v, dict):
#             items.extend(flatten_keys(v, new_key))
#         else:
#             items.append(new_key)
#     return items

# def get_value_from_path(data, path):
#     """Hole Wert anhand Pfad mit Punkt-Notation"""
#     for part in path.split("."):
#         if isinstance(data, dict) and part in data:
#             data = data[part]
#         else:
#             return None
#     return data

# #Neu:
# async def async_setup_entry(hass, entry, async_add_entities):
#     ip = entry.data["IP-Address"]
#     name = entry.data["Name"]
#     update_interval = entry.data.get("Interval", 15)
#     selected_groups = entry.data["selected_groups"]

#     entities = []
#     session = async_get_clientsession(hass)

#     url = f"http://{ip}/"
#     try:
#         async with session.get(url, timeout=5, ssl=False) as resp:
#             data = await resp.json()

#         sbi = data.get("SBI", {})
#         uid = sbi.get("UID", "unknown")
#         version = sbi.get("Ver", "unknown")

#         # Nur die ausgewählten Keys verwenden
#         for key in selected_groups:
#             if key in ("UID", "Ver"):
#                 continue
#             group = key.split(".")[0]
#             entities.append(SnettboxHaSensor(hass, name, group, key, ip, update_interval, uid, version))

#     except Exception as e:
#         _LOGGER.error(f"Fehler beim Abrufen der JSON-Daten: {e}")

#     async_add_entities(entities, True)



# class SnettboxHaSensor(Entity):
#     def __init__(self, hass, base_name, group, key, ip, update_interval, uid, version):
#         self._hass = hass
#         self._base_name = base_name
#         self._group = group
#         self._key = key
#         self._ip = ip
#         self._uid = uid
#         self._version = version
#         self._state = None
#         self._unsub_update = None
#         self._update_interval = timedelta(seconds=update_interval)

#         key_short = key[len(group) + 1:] if key.startswith(group + ".") else key
#         self._name = f"{base_name} {key_short}"

#     @property
#     def name(self):
#         return self._name

#     @property
#     def state(self):
#         return self._state

#     @property
#     def unique_id(self):
#         return f"{self._ip}_{self._group}_{self._key}"

#     @property
#     def should_poll(self):
#         return False

#     @property
#     def icon(self):
#         return ICON_MAP.get(self._key)

#     @property
#     def device_info(self):
#         return {
#             "identifiers": {(DOMAIN, self._uid)},
#             "name": self._base_name,
#             "manufacturer": "battery-direct",
#             "model": "Snettbox",
#             "sw_version": self._version,
#         }

#     async def async_added_to_hass(self):
#         self._unsub_update = async_track_time_interval(
#             self._hass, self.async_update, self._update_interval
#         )
#         await self.async_update()

#     async def async_will_remove_from_hass(self):
#         if self._unsub_update:
#             self._unsub_update()
#             self._unsub_update = None

#     async def async_update(self, now=None):
#         url = f"http://{self._ip}/"
#         session = async_get_clientsession(self._hass)
#         try:
#             # Deaktiviere SSL-Prüfung für Geräte mit fehlerhafter/fehlender TLS-Konfiguration
#             async with session.get(url, timeout=5, ssl=False) as resp:
#                 data = await resp.json()

#             sbi = data.get("SBI", {})
#             self._state = get_value_from_path(sbi, self._key)
#             self.async_write_ha_state()
#         except Exception as e:
#             _LOGGER.error(f"Fehler beim Abrufen der JSON-Daten: {e}")
#             self._state = None

#Neu generiert von 
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_interval
from datetime import timedelta
from .const import DOMAIN, DEFAULT_URL
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


class SnettboxHaSensor(Entity):
    """Sensor für einzelne ausgewählte Werte der Snettbox"""

    def __init__(self, hass, base_name, group, key, ip, update_interval, uid, version):
        self._hass = hass
        self._base_name = base_name
        self._group = group
        self._key = key
        self._ip = ip
        self._uid = uid
        self._version = version
        self._state = None
        self._unsub_update = None
        self._update_interval = timedelta(seconds=update_interval)

        # Friendly Name, z.B. "Temp (SB)" oder "UID (Device)"
        key_short = key[len(group)+1:] if key.startswith(group + ".") else key
       #self._name = f"{key_short} ({group})"
        self._name = f"{group}:{key_short}"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

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
        }

    async def async_added_to_hass(self):
        self._unsub_update = async_track_time_interval(
            self._hass, self.async_update, self._update_interval
        )
        await self.async_update()

    async def async_will_remove_from_hass(self):
        if self._unsub_update:
            self._unsub_update()
            self._unsub_update = None

    async def async_update(self, now=None):
        session = async_get_clientsession(self._hass)
        url = DEFAULT_URL.format(ip=self._ip)
        try:
            async with session.get(url, timeout=5, ssl=False) as resp:
                data = await resp.json()

            sbi = data.get("SBI", {})
            if not sbi:
                _LOGGER.debug("async_update: keine 'SBI' Daten von %s (%s)", self._ip, url)
                self._state = "unbekannt"
                self.async_write_ha_state()
                return

            value = get_value_from_path(sbi, self._key)
            self._state = value if value is not None else "unbekannt"
            self.async_write_ha_state()

        except Exception as e:
            _LOGGER.error(f"Fehler beim Abrufen der JSON-Daten für {self._key}: {e}")
            self._state = "unbekannt"


async def async_setup_entry(hass, entry, async_add_entities):
    """Erstelle Sensoren basierend auf den ausgewählten Checkboxen im ConfigFlow"""
    ip = entry.data["IP-Address"]
    name = entry.data["Name"]
    update_interval = entry.data.get("Interval", 15)
    selected_groups = entry.data["selected_groups"]

    entities = []
    session = async_get_clientsession(hass)

    url = DEFAULT_URL.format(ip=ip)
    try:
        async with session.get(url, timeout=5, ssl=False) as resp:
            data = await resp.json()

        sbi = data.get("SBI", {})
        if not sbi:
            _LOGGER.warning("Keine 'SBI' Daten in Antwort von %s gefunden (evtl. falscher Pfad). URL: %s", ip, url)
            async_add_entities(entities, True)
            return
        uid = sbi.get("UID", "unknown")
        version = sbi.get("Ver", "unknown")

        # UID und Ver als eigene Sensoren
        entities.append(SnettboxHaSensor(hass, name, "Device", "UID", ip, update_interval, uid, version))
        entities.append(SnettboxHaSensor(hass, name, "Device", "Ver", ip, update_interval, uid, version))

        # Ausgewählte Keys
        for key in selected_groups:
            if key in ("UID", "Ver"):
                continue
            group = key.split(".")[0]
            entities.append(SnettboxHaSensor(
                hass, name, group, key, ip, update_interval, uid, version
            ))

        # Alphabetisch nach Gruppe und Key sortieren
        entities.sort(key=lambda e: (e._group, e._key))

    except Exception as e:
        _LOGGER.error(f"Fehler beim Abrufen der JSON-Daten: {e}")

    async_add_entities(entities, True)
