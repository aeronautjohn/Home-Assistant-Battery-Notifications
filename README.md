# Home-Assistant-Battery-Notifications
A simple script for Home Assistant (using AppDaemon) to send notifications to your devices in the event that any battery exposed to Home Assistant dips below the configured threshold.

The script listens for any device which has the `device_class` flag of `battery` configured. This means not only device batteries like smartphones and tablets; but also all of those little wireless sensors and switches and the like!

## Installation

1. Install the AppDaemon Add-On, if you don't have it already.

2. In the AppDaemon apps folder (default: `/addon_configs/xxxxxxxx_appdaemon/apps`), copy `battery_notifications.py`

3. In the same AppDaemon apps folder, edit `apps.yaml` and add the following:

```
battery_notifications:
  module: battery_notifications
  class: BatteryNotifications
  notification_threshold: 30
  reset_threshold: 50
  notification_services:
    - notify.notify_all
  blacklist: []
```

## Configuration

`notification_threshold` Sets the point below which you will receive notifications.

`reset_threshold` The app will only send you one notification. Once the battery has recovered to this threshold, the notification will be 'armed' again and will be sent again once it drops below the `notification_threshold` again.

`notification_services` Add your notification entities here. Though I recommend using a notification group, such as the example `notify.notify_all` in your `configuration.yaml` This way, devices can be added or changed without having to change every script and automation that uses them.

`blacklist` If there are devices you don't want to be alerted in the event, add them here. For example

```
  blacklist:
    - sensor.some_device
```

## Example notification group

Add the following to `configuration.yaml`

```
notify:
  - platform: group
    name: notify_all
    unique_id: notify_all
    services:
      - service: mobile_app_1
      - service: mobile_app_2
      - service: some_other_device
```


