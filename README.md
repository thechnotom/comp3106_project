# comp3106_project

COMP 3106 A Final Project

A simulator to demonstrate how multiple species behave when competing for a limited resource.

Technical requirements:
- Testing was conducted using Python 3.10.0 (although any Python 3 version should be sufficient)
- The matplotlib library is necessary to generate graphs
  - Install with the following: pip3 install matplotlib

The simulator can be run by using the following command (Windows PowerShell):
py .\main.py <config>

Necessary configuration files:
- config.json (or alternative provided on the command line)
- initial_conditions/basic_start.csv (or alternative provided in the configuration file)

The configuation file is in JSON format. The file "config_description.json" describes how each field is used.
Note that a species' name must be only a single character that is not used for another purpose.