from wordpot.plugins_manager import BasePlugin
import re

import datetime

TIMTHUMB_RE     = re.compile('[tim]*thumb|uploadify', re.I)

class Plugin(BasePlugin):
    def run(self):
        # Logic
        if TIMTHUMB_RE.search(self.inputs['subpath']) is not None:
            # Message to log
            log = '%s probed for timthumb: %s' % (self.inputs['request'].remote_addr, self.inputs['subpath'])
            self.outputs['log'] = log
            self.outputs['log_json'] = self.to_json_log(filename=self.inputs['subpath'], plugin='timthumb')
            if 'theme' in self.inputs:
                self.outputs['log_postgresql_themes_probes'] = {"source_ip": self.inputs['request'].remote_addr,"source_port": self.inputs['request'].environ['REMOTE_PORT'],"dest_host": self.inputs['request'].environ['SERVER_NAME'],"dest_port": self.inputs['request'].environ['SERVER_PORT'],"probed_theme": self.inputs['theme'],"path": self.inputs['subpath'],"user_agent": self.inputs['request'].user_agent.string,"url": self.inputs['request'].url,"timestamp": str(datetime.datetime.now())}

            if 'plugin' in self.inputs:
                self.outputs['log_postgresql_plugins_probes'] = {"source_ip": self.inputs['request'].remote_addr,"source_port": self.inputs['request'].environ['REMOTE_PORT'],"dest_host": self.inputs['request'].environ['SERVER_NAME'],"dest_port": self.inputs['request'].environ['SERVER_PORT'],"probed_plugin": self.inputs['plugin'],"path": self.inputs['subpath'],"user_agent": self.inputs['request'].user_agent.string,"url": self.inputs['request'].url,"timestamp": str(datetime.datetime.now())}

            # Template to render
            self.outputs['template'] = 'timthumb.html'

        return
