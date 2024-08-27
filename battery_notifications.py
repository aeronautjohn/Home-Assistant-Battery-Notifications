import appdaemon.plugins.hass.hassapi as hass
import json
import os

class BatteryNotifications(hass.Hass):
    """
    A class to manage battery level notifications in Home Assistant.
    It monitors battery levels of devices and sends notifications when they fall below a certain threshold.
    """

    def initialize(self):
        """
        Initialize the BatteryNotifications app.
        Sets up configuration parameters, loads persistent state, and starts listening for state changes.
        """
        # Set notification threshold, defaulting to 30% if not specified
        self.notification_threshold = self.args.get("notification_threshold", 30)
        # Set reset threshold, defaulting to 50% if not specified
        self.reset_threshold = self.args.get("reset_threshold", 50)
        # Set notification services, defaulting to notify.notify_all if not specified
        self.notification_services = self.args.get("notification_services", ["notify.notify_all"])
        # Set blacklist of entities to ignore, defaulting to an empty list if not specified
        self.blacklist = self.args.get("blacklist", [])
        if not isinstance(self.blacklist, list):
            self.blacklist = []
        
        # Set up persistent storage file path
        self.persistent_file = os.path.join("/config/apps/storage", "battery_notifications_state.json")
        # Load the list of batteries that have already been notified
        self.notified_batteries = self.load_persistent_state()
        
        # Start listening for state changes on all sensor entities
        self.listen_state(self.check_battery_level, "sensor")

    def load_persistent_state(self):
        """
        Load the persistent state from a JSON file.
        
        Returns:
            list: A list of entity_ids for which notifications have been sent.
        """
        if os.path.exists(self.persistent_file):
            with open(self.persistent_file, 'r') as f:
                return json.load(f)
        return []

    def save_persistent_state(self):
        """
        Save the current state (list of notified batteries) to a JSON file.
        Creates the directory if it doesn't exist.
        """
        self.log(f"Attempting to save state to: {self.persistent_file}", level="DEBUG")
        os.makedirs(os.path.dirname(self.persistent_file), exist_ok=True)
        with open(self.persistent_file, 'w') as f:
            json.dump(self.notified_batteries, f)
        self.log("State saved successfully", level="DEBUG")

    def check_battery_level(self, entity, attribute, old, new, kwargs):
        """
        Check the battery level of a sensor entity and send a notification if it's low.
        
        Args:
            entity (str): The entity_id of the sensor.
            attribute (str): The changed attribute (not used in this method).
            old (str): The old state value (not used in this method).
            new (str): The new state value (not used in this method).
            kwargs (dict): Additional keyword arguments (not used in this method).
        """
        # Skip blacklisted entities
        if entity in self.blacklist:
            return

        # Check if the entity is a battery sensor
        device_class = self.get_state(entity, attribute="device_class")
        if device_class == "battery":
            battery_level = self.get_state(entity)

            if battery_level not in [None, "unavailable", "unknown"]:
                try:
                    battery_level = float(battery_level)

                    if battery_level < self.notification_threshold:
                        # Send notification if battery is low and hasn't been notified before
                        if entity not in self.notified_batteries:
                            self.log(f"Low battery detected for {entity}. Saving state.", level="DEBUG")
                            message = f"Home Assistant has detected a low battery. {self.friendly_name(entity)} is at {int(battery_level)}%."
                            for service in self.notification_services:
                                domain, service_name = service.split(".")
                                self.call_service(f"{domain}/{service_name}", message=message)
                            self.notified_batteries.append(entity)
                            self.save_persistent_state()
                    elif battery_level > self.reset_threshold:
                        # Remove entity from notified list if battery level is above reset threshold
                        if entity in self.notified_batteries:
                            self.notified_batteries.remove(entity)
                            self.save_persistent_state()
                except (ValueError, TypeError) as e:
                    self.log(f"Error converting battery level '{battery_level}' for entity '{entity}': {e}", level="ERROR")

    def friendly_name(self, entity):
        """
        Get the friendly name of an entity.
        
        Args:
            entity (str): The entity_id.
        
        Returns:
            str: The friendly name of the entity.
        """
        return self.get_state(entity, attribute="friendly_name")
