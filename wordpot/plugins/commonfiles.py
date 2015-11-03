from wordpot.plugins_manager import BasePlugin

import datetime

class Plugin(BasePlugin):
    def run(self):
        # Initialize template vars dict 
        self.outputs['template_vars'] = {} 

        # Common files:
        # Real File -> Template
        common = {
                'readme.html': 'readme.html',
                'xmlrpc.php' : 'xmlrpc.html'
                 }
        
        # Logic
        origin = self.inputs['request'].remote_addr
        if self.inputs['filename'] is not None and self.inputs['ext'] is not None:
            filename = self.inputs['filename'] + '.' + self.inputs['ext']

            if filename in common:
                self.outputs['log'] = '%s probed for: %s' % (origin, filename)
                self.outputs['log_json'] = self.to_json_log(filename=filename, plugin='commonfiles')
                self.outputs['log_postgresql'] = "INSERT INTO file_probes (plugin, source_ip, source_port, dest_host, dest_port, probed_filename, user_agent, url, timestamp) VALUES ('commonfiles','%s',%s,'%s',%s,'%s','%s','%s','%s')" % (self.inputs['request'].remote_addr, self.inputs['request'].environ['REMOTE_PORT'], self.inputs['request'].environ['SERVER_NAME'], self.inputs['request'].environ['SERVER_PORT'], filename, self.inputs['request'].user_agent.string, self.inputs['request'].url, str(datetime.datetime.now()))
                self.outputs['template'] = common[filename]

        return
