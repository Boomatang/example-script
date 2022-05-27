import os
import toml
import yaml
from pathlib import Path

with open("settings.toml", "r") as f:
    settings = toml.loads(f.read())

severity = [s.lower() for s in settings["alerts"]["severity"]]
alerts_path = Path(settings["alerts"]["path"])
alerts = {}
levels = []

if not alerts_path.is_dir():
    print("Alerts directory does not exist")
    exit(1)

for root, dirs, files in os.walk(alerts_path):
    dirs[:] = [d for d in dirs if d not in settings["alerts"]["exclude_dir"]]
    for name in files:
        if name in settings['alerts']['exclude_files']:
            continue
        entry = Path(root, name)
        if entry.suffix.lower() != ".yaml":
            continue

        with open(entry, "r") as f:
            data = yaml.safe_load(f)
        if "kind" not in data or data["kind"] != "PrometheusRule":
            continue

        alerts.setdefault(name, {"path": entry, "severity": {}})
        
        for group in data['spec']['groups']:
            for rule in group["rules"]:
                if "labels" in rule and rule["labels"] is not None:
                    if "severity" in rule["labels"] and rule["labels"]["severity"].lower() in severity:
                        if rule["labels"]["severity"] in alerts[name]["severity"]:
                            alerts[name]["severity"][rule["labels"]["severity"]].append(rule["alert"])
                        else:
                            alerts[name]["severity"].setdefault(rule["labels"]["severity"], [rule["alert"]])

tests_path = Path(settings["test"]["path"])
if not tests_path.is_dir():
    print("Tests directory does not exist")
    exit(1)

for root, dirs, files in os.walk(tests_path):
    dirs[:] = [d for d in dirs if d not in settings["tests"]["exclude_dir"]]
    for name in files:
        entry = Path(root, name)
        if entry.suffix.lower() != ".yaml":
            continue

        with open(entry, "r") as f:
            data = yaml.safe_load(f)
        if "rule_files" not in data:
            continue

        for test in data['tests']:
            if "alert_rule_test" in test:
                for rule in test["alert_rule_test"]:
                    for exp_alert in rule['exp_alerts']:
                        if 'exp_labels' in exp_alert and 'alertname' in exp_alert['exp_labels']:
                            for key, item in alerts.items():
                                if exp_alert['exp_labels']['severity'].lower() in item['severity'] \
                                        and exp_alert['exp_labels']['alertname'] in item['severity'][exp_alert['exp_labels']['severity'].lower()]:
                                    item['severity'][exp_alert['exp_labels']['severity'].lower()].remove(exp_alert['exp_labels']['alertname'])
                                else:
                                    levels.append(exp_alert['exp_labels']['severity'].lower())

print("Rule files checked:")
[print(f"\t{alert}") for alert in alerts]
print()

print("Missing Tests Results Summary")
for level in severity:
    counter = 0
    for key, item in alerts.items():
        if level in item['severity']:
            counter += len(item['severity'][level])
    print(f"\t{level}: {counter}")
print()

print("Alerts with missing test by severity")
for level in severity:
    print(f"\t{level}")
    for key, item in alerts.items():
        if level in item['severity'] and len(item['severity'][level]) > 0:
            print(f"\t\tFile: {key}")
            for alert in item['severity'][level]:
                print(f"\t\t\t{alert}")
print()

levels = set(levels)
fail_levels = set(settings['script']['fail_levels'])

if levels.intersection(fail_levels):
    print("Failing exit condition met.")
    exit(1)
