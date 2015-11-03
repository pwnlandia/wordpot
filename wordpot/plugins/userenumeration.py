from wordpot.plugins_manager import BasePlugin
from wordpot import app

import datetime

class Plugin(BasePlugin):
    def run(self):
        # Initialize template vars dict 
        self.outputs['template_vars'] = {} 

        # Logic
        origin = self.inputs['request'].remote_addr
        req_args = self.inputs['request'].args 

        if 'author' in req_args:
            for k, a in enumerate(app.config['AUTHORS']):
                if (k + 1) == int(req_args['author']):
                    self.outputs['log'] = '%s probed author page for user: %s' % (origin, a)
                    self.outputs['log_json'] = self.to_json_log(author=a, plugin='userenumeration')
                    self.outputs['log_postgresql'] = "INSERT INTO author_probes (plugin, source_ip, source_port, dest_host, dest_port, probed_author, user_agent, url, timestamp) VALUES ('userenumeration','%s',%s,'%s',%s,'%s','%s','%s','%s')" % (self.inputs['request'].remote_addr, self.inputs['request'].environ['REMOTE_PORT'], self.inputs['request'].environ['SERVER_NAME'], self.inputs['request'].environ['SERVER_PORT'], a, self.inputs['request'].user_agent.string, self.inputs['request'].url, str(datetime.datetime.now()))
                    self.outputs['template_vars']['AUTHORPAGE'] = True
                    self.outputs['template_vars']['CURRENTAUTHOR'] = (k+1, a)
                    self.outputs['template'] = app.config['THEME'] + '.html'

        return 
