import appdaemon.plugins.hass.hassapi as hass

class BatteryNotifications(hass.Hass):

    def initialize(self):
        self.notified_batteries = []
        self.notification_threshold = self.args.get("notification_threshold", 30)
        self.reset_threshold = self.args.get("reset_threshold", 50)
        self.notification_services = self.args.get("notification_services", ["notify.notify_all"])
        self.blacklist = self.args.get("blacklist", [])
        if not isinstance(self.blacklist, list):
            self.blacklist = []
        self.listen_state(self.check_battery_level, "sensor")

    def check_battery_level(self, entity, attribute, old, new, kwargs):
        if entity in self.blacklist:
            return

        device_class = self.get_state(entity, attribute="device_class")
        if device_class == "battery":
            battery_level = self.get_state(entity)

            if battery_level not in [None, "unavailable", "unknown"]:
                try:
                    battery_level = float(battery_level)

                    if battery_level < self.notification_threshold:
                        if entity not in self.notified_batteries:
                            message = f"Home Assistant has detected a low battery. {self.friendly_name(entity)} is at {int(battery_level)}%."
                            for service in self.notification_services:
                                domain, service_name = service.split(".")
                                self.call_service(f"{domain}/{service_name}", message=message)
                            self.notified_batteries.append(entity)
                    elif battery_level > self.reset_threshold:
                        if entity in self.notified_batteries:
                            self.notified_batteries.remove(entity)
                except (ValueError, TypeError) as e:
                    self.log(f"Error converting battery level '{battery_level}' for entity '{entity}': {e}", level="ERROR")

    def friendly_name(self, entity):
        return self.get_state(entity, attribute="friendly_name")
