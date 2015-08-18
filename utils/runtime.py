import subprocess
import StringIO

def execute (program):
    '''
        Args:
            program - A list that contains the command for executing.

        Returns:
            A StringIO instance that contains the result of execution.
            
        Raises:
            IOError - Cannot send the command.
    '''
    try:
        proc = subprocess.Popen(program, stdout=subprocess.PIPE)
        process_res = proc.communicate()
        # Use StringIO to format the response into lines.
        return StringIO.StringIO(process_res[0])
    except OSError, e:
        print e.output
        raise IOError()
    except ValueError, e:
        print e.output
        raise IOError()
    except subprocess.CalledProcessError,e:
        print e.output
        raise IOError()