from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry):
    ip = entry.data["IP-Address"]
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "ip": ip
    }

# hass.async_create_task(
#     hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
# )
# Korrekte Methode: await verwenden
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

# Wenn alles erfolgreich war, True zurückgeben
    return True

async def async_unload_entry(hass, entry):
    await hass.config_entries.async_forward_entry_unload(entry, ["sensor"])
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
