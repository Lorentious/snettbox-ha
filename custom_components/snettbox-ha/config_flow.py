from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, DEFAULT_URL
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import async_timeout
import logging

_LOGGER = logging.getLogger(__name__)

# mache aus dem verschachtelten json eine flache Liste
def flatten_dict_keys(d, parent_key="", sep="."):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict_keys(v, new_key, sep=sep))
        else:
            items.append(new_key)
    return items

class SnettboxHaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    def __init__(self):
        self.ip = None
        self.name = None
        self.available_groups = []

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self.ip = user_input["IP-Address"]
            self.name = user_input["Name"]
            self.update_interval = user_input.get("Interval", 15)
            session = async_get_clientsession(self.hass)
            url = DEFAULT_URL.format(ip=self.ip)

#Verbindungsaufbau zur Snettbox um die verfügbaren Gruppen auszulesen
            try:
                async with async_timeout.timeout(5):
                    resp = await session.get(url)
                    resp.raise_for_status()
                    data = await resp.json()
                sbi = data.get("SBI", {})

                # UID und Ver aus der Auswahl rausfiltern, UID, Ver werden separat genutzt (Anzeige links)
                #self.available_groups = [grp for grp in sbi.keys() if grp not in ("UID", "Ver")]

                # 🔍 Verschachtelte Keys auflösen
                all_keys = flatten_dict_keys(sbi)


                self.available_groups = [
                         grp for grp in flatten_dict_keys(sbi)
                        if not grp.endswith(("UID", "Ver"))
]


         # hier wird dem User die Auswahl angezeigt und gewartet auf Eingabe     
                return await self.async_step_select_groups()
            
         # Ausnahme abfangen, wenn was schiefgeht   
            except Exception as e:
                _LOGGER.error(f"Cannot connect to {url}: {e}")
                return self.async_show_form(
                    step_id="user",
                    data_schema=vol.Schema({
                        vol.Required("IP-Address"): str,
                        vol.Required("Name"): str,
                        vol.Required("Interval", default=15): int,
                    }),
                    errors={"base": "cannot_connect"}
                )

# Ausgabe der Form zur Eingabe der Werte IP, Name und Intervall
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("IP-Address"): str,
                vol.Required("Name"): str,
                vol.Required("Interval", default=15): int,
            })
        )
    
# speichert die ausgewählten Gruppen und erstellt den Eintrag
    async def async_step_select_groups(self, user_input=None):
        if user_input is not None:
            selected_groups = [grp for grp, val in user_input.items() if val]

            # UID und Ver immer automatisch hinzufügen
            selected_groups += ["UID", "Ver"]

        #beendet und speichert die Eingaben in HA
            return self.async_create_entry(
                title=self.name,
                data={
                    "IP-Address": self.ip,
                    "Name": self.name,
                    "Interval": self.update_interval,
                    "selected_groups": selected_groups,
                }
            )
        #Erstellung des Auswahlformulars für die Gruppen
        #schema = vol.Schema({
        #    vol.Optional(group): bool for group in self.available_groups
        #})

        schema = vol.Schema({
            vol.Optional(group, description={"suggested_value": group.replace(".", " → ")}): bool
            for group in self.available_groups
        })

        #Anzeige des Auswahlformulars für die Gruppen
        return self.async_show_form(
            step_id="select_groups",
            data_schema=schema,
        )
