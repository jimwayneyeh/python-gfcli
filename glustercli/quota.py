import subprocess
import logging
import StringIO

class Quota:
    '''
        Class for operating the directory quota to a specified GlusterFS volume.
    '''
    
    def __init__ (self, volume_name):
        self._log = logging.getLogger("gfs.glustercli.quota")
        self._log.debug("Initiate the template of command.")
        
        self.program = ["/usr/sbin/gluster", 
                        "volume", 
                        "quota",
                        volume_name,
                        "list"]
    
    def get_dir_quota (self, dir_name):
        self._log.debug("Get the quota for directory '%s'" % dir_name)
        
        # Send the command to GlusterFS CLI.
        try:
            self._log.debug("Try to execute the command %s." % self.program)
            proc = subprocess.Popen(self.program, stdout=subprocess.PIPE)
            process_res = proc.communicate()
        except OSError, e:
            print e.output
            raise
        except ValueError, e:
            print e.output
            raise
        except subprocess.CalledProcessError,e:
            print e.output
            raise
        
        '''
            Parse the response from the command line of GlusterFS client.
        '''
        # Use StringIO to format the response into lines.
        buf = StringIO.StringIO(process_res[0])
        
        # Ensure the format of directory name to "/....".
        if not dir_name.startswith("/"):
            dir_name = "/%s" % dir_name
        
        # Read each of responded lines and try to find out the description about the directory specified by the parameter 'dir_name'. 
        while True:
            line = buf.readline()
            
            # Break the loop if the end of the response is reached.
            if line == "":
                break
            
            # Get the line which describe the specified directory and return the content in list format.
            if line.startswith(dir_name):
                tokens = line.split()
                self._log.debug("Tokenize: %s" % line.split())
                
                # Convert the response of "Yes"/"No" to "True"/"False" for software limit.
                if tokens[5] == "No":
                    soft_exceeded = False
                else:
                    soft_exceeded = True
                self._log.debug("Soft-limit: %s" % soft_exceeded)
                    
                # Convert the response of "Yes"/"No" to "True"/"False" for hardware limit.
                if tokens[6] == "No":
                    hard_exceeded = False
                else:
                    hard_exceeded = True
                self._log.debug("Hard-limit: %s" % hard_exceeded)
                
                self._log.debug("Try to convert used: %d" % self._format_quota(tokens[3]))
                self._log.debug("Try to convert Available: %d" % self._format_quota(tokens[4]))
                
                return [
                        tokens[0],      # Name of the directory
                        self._format_quota(tokens[1]),  # Hard-limit
                        tokens[2],      # Soft-limit
                        self._format_quota(tokens[3]),  #Used
                        self._format_quota(tokens[4]),  #Available
                        soft_exceeded,  # Soft-limit
                        hard_exceeded   # Hard-limit
                    ]
                
    def _format_quota (self, quota):
        '''
            Convert the specified quota from "..TB", "..GB", "..MB", or "..KB" to an integer in bytes.
        '''
        if quota.endswith("TB"):
            return int(float(quota[:-2]) * 1099511627776)
        elif quota.endswith("GB"):
            return int(float(quota[:-2]) * 1073741824)
        elif quota.endswith("MB"):
            return int(float(quota[:-2]) * 1048576)
        elif quota.endswith("KB"):
            return int(float(quota[:-2]) * 1024)
        else:
            raise ValueError()
        
        