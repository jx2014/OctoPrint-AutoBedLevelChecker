# coding=utf-8
from __future__ import absolute_import

### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.

import octoprint.plugin
import logging


class AutobedlevelcheckerPlugin(octoprint.plugin.StartupPlugin,
                                octoprint.plugin.TemplatePlugin,
                                octoprint.plugin.SettingsPlugin,
                                octoprint.plugin.AssetPlugin,
                                octoprint.plugin.SimpleApiPlugin,
                                ):

    def __init__(self):
        self._logger = logging.getLogger("octoprint.plugins.AutoBedLevelChecker")
        self._logger.info("this is AutoBedLevelChecker init func")

    def on_after_startup(self):
        self._logger.info("### Auto Bed Level Checker Plugin ###")

    ##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return dict(
            # put your plugin's default settings here/
            max_diff=1 # maximum value auto bed level can tolerate
        )

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=False)
        ]

    ##~~ AssetPlugin mixin

    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return dict(
            js=["js/AutoBedLevelChecker.js"],
            css=["css/AutoBedLevelChecker.css"],
            less=["less/AutoBedLevelChecker.less"]
        )

    ##~~ Softwareupdate hook

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return dict(
            AutoBedLevelChecker=dict(
                displayName="Auto bed level checker",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="jx2014",
                repo="OctoPrint-AutoBedLevelChecker",
                current=self._plugin_version,

                # update method: pip
                pip="https://github.com/jx2014/OctoPrint-AutoBedLevelChecker/archive/{target_version}.zip"
            )
        )

    def message_on_connect(self, comm, script_type, script_name, *args, **kwargs):
        if not script_type == "gcode" or not script_name == "afterPrinterConnected":
            return None
        self._logger.info("### inside message_on_connect ###")
        prefix = None
        postfix = "M117 OctoPrint connected"
        return prefix, postfix

    # tutorial - simple api plugin
    # https://docs.octoprint.org/en/master/plugins/mixins.html#simpleapiplugin
    def get_api_commands(self):
        return dict(
            command1=[],
            command2=["some_parameter"]
        )

    def on_api_command(self, command, data):
        import flask
        if command == "command1":
            parameter = "unset"
            if "parameter" in data:
                parameter = "set"
            self._logger.info("command1 called, parameter is {parameter}".format(**locals()))
        elif command == "command2":
            self._logger.info("command2 called, some_parameter is {some_parameter}".format(**data))

    def on_api_get(self, request):
        return flask.jsonify(foo="bar")

    def gcode_processor(comm, line, *args, **kwargs):
        if "MACHINE_TYPE" not in line:
            return line

        from octoprint.util.comm import parse_firmware_line

        # Create a dict with all the keys/values returned by the M115 request
        printer_data = parse_firmware_line(line)

        logging.getLogger("octoprint.plugin." + __name__).info(
            "Machine type detected: {machine}.".format(machine=printer_data["firmware_name"]))

        return line

# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Autobedlevelchecker Plugin"

# Starting with OctoPrint 1.4.0 OctoPrint will also support to run under Python 3 in addition to the deprecated
# Python 2. New plugins should make sure to run under both versions for now. Uncomment one of the following
# compatibility flags according to what Python versions your plugin supports!
# __plugin_pythoncompat__ = ">=2.7,<3" # only python 2
# __plugin_pythoncompat__ = ">=3,<4" # only python 3
__plugin_pythoncompat__ = ">=2.7,<4"  # python 2 and 3


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = AutobedlevelcheckerPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
        #"octoprint.comm.protocol.scripts": __plugin_implementation__.message_on_connect,
        "octoprint.comm.protocol.gcode.received": __plugin_implementation__.gcode_processor,
    }
