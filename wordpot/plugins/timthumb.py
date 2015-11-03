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
                self.outputs['log_postgresql'] = "INSERT INTO themes_probes (plugin, source_ip, source_port, dest_host, dest_port, probed_theme, path, user_agent, url, timestamp) VALUES ('timthumb','%s',%s,'%s',%s,'%s','%s','%s','%s','%s')" % (self.inputs['request'].remote_addr, self.inputs['request'].environ['REMOTE_PORT'], self.inputs['request'].environ['SERVER_NAME'], self.inputs['request'].environ['SERVER_PORT'], self.inputs['theme'], self.inputs['subpath'], self.inputs['request'].user_agent.string, self.inputs['request'].url, str(datetime.datetime.now()))

            if 'plugin' in self.inputs:
                self.outputs['log_postgresql'] = "INSERT INTO plugins_probes (plugin, source_ip, source_port, dest_host, dest_port, probed_plugin, path, user_agent, url, timestamp) VALUES ('timthumb','%s',%s,'%s',%s,'%s','%s','%s','%s','%s')" % (self.inputs['request'].remote_addr, self.inputs['request'].environ['REMOTE_PORT'], self.inputs['request'].environ['SERVER_NAME'], self.inputs['request'].environ['SERVER_PORT'], self.inputs['plugin'], self.inputs['subpath'], self.inputs['request'].user_agent.string, self.inputs['request'].url, str(datetime.datetime.now()))

            # Template to render
            self.outputs['template'] = 'timthumb.html'

        return
