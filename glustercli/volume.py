import logging
import StringIO
import re
from utils import runtime

class Volume:
    def __init__ (self, volume_name):
        self._log = logging.getLogger("gfs.glustercli.volume")
        
        self.program = ["/usr/sbin/gluster", 
                        "volume", 
                        "info",
                        volume_name]


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
        '''
            Get the quota information of a specified directory.
            
            Args:
                dir_name - Name of the directory for checking the quota.

            Return:
                A list in following format:
                [ directory_name, hard_limit (bytes), soft_limit, used (bytes), available (bytes), 
                    exceed_hard_limit (boolean), exceed_soft_limit (boolean) ]
                None is returned if the specified directory has no quota limitation.

            Raises:
                None.
        '''
        self._log.debug("Get the quota for directory '%s'" % dir_name)
        
        # Send the command to GlusterFS CLI.
        buf = runtime.execute(self.program)
        
        '''
            Parse the response from the command line of GlusterFS client.
        '''
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
            
        return None
                
    def _format_quota (self, quota):
        '''
            Convert the specified quota from "..TB", "..GB", "..MB", or "..KB" to an integer in bytes.
            
            Args:
                quota - A quota description returned by the GlusterFS CLI. The format should be like "256GB".

            Returns:
                An integer which represents the quota in bytes. 

            Raises:
                ValueError - Invalid format of the input parameter.
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
        
        