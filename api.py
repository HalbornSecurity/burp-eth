import os

class Command:

    @classmethod
    def execute(cls, format_name = None, command = None, arguments = None):
        result = {}
        result['error'] = 'operation failed'
        result['data'] = None

        if command and format_name:
            command = command.lower()
            format_name = format_name.lower()

            if os.path.isfile("./lib/{:s}.py".format(format_name)):
                try:
                    format = __import__(format_name)
                    execute_command = getattr(format, command)

                    try:
                        response = execute_command(arguments)
                        
                        if not response['error']:
                            result['error'] = None
                            result['data'] = response['data']
                        else:
                            result['error'] = response['error']
                    except Exception as error:
                        result['error'] = str(error)
                except Exception as error:
                    result['error'] = str(error)
            else:
                result['error'] = "format \"{:s}\" unsupported"
        else:
            result['error'] = "command/format missing"

        return result