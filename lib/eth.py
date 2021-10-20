import urllib
from com.esaulpaugh.headlong.util import FastHex
from com.esaulpaugh.headlong.abi import Function
from com.esaulpaugh.headlong.util import Strings;
from com.esaulpaugh.headlong.util import SuperSerial; 
import simplejson

TYPE_TX = 'tx'
TYPE_DATA = 'data'
SUPPORTED_COMMANDS = [
    'encode',
    'decode'
]
API_URL = 'https://www.4byte.directory/api/v1/'
API_ENDPOINT_SIGNATURES = 'signatures/'
API_GET_PARAM_HEX_SIGNATURE = 'hex_signature'
HEX_SIGNTURE_LENGTH = 8
PREFIX_LENGTH = 2
HEX_ADDRESS_LENGTH = 43
JAVA_ITERABLE_TUPLE = 'tuple'
JAVA_ITERABLE_ARRAY = 'array'
JAVA_ITERABLES_LOWERCASE = [JAVA_ITERABLE_ARRAY, JAVA_ITERABLE_TUPLE]
CHAR_DOUBLE_QUOTE = '"'
CHAR_SINGLE_QUOTE = '\''
HEX_PREFIX = '0x'

def encode(arguments = None):
    result = {}
    result['error'] = 'encoding failed'
    result['data'] = {}
    args = _parse_args_for_codec(arguments)

    if not args['error']:
        input_type, abi, input_data = args['data']

        if type:
            if input_type == TYPE_TX:
                # TODO: implement
                pass
            elif input_type == TYPE_DATA:
                if abi:
                    # abi was provided by user
                    abi = abi.strip()
                    
                    # replace parenthesis with brackets
                    input_data = "[{}]".format(input_data[1:-1])

                    try:
                        # try parsing the signature
                        signature = Function.parse(abi)
                    except:
                        result['error'] = "parsing abi failed"

                        return result
                    try:
                        # try parsing the input to json    
                        input_data = simplejson.loads(input_data)
                    except:
                        result['error'] = "parsing input data from string failed"

                        return result
                    try:
                        # encode all params
                        input_data = _parse_params_for_encode(input_data)
                    except:
                        result['error'] = "parsing params failed"

                        return result
                    try:
                        # parse to json and format the encoded input data
                        input_data =  "({})".format(simplejson.dumps(input_data)[1:-1]).replace(CHAR_DOUBLE_QUOTE, CHAR_SINGLE_QUOTE)
                    except:
                        result['error'] = "parsing params to string failed"

                        return result
                    try:
                        output = signature.encodeCall(SuperSerial.deserialize(signature.getInputs(), input_data, False))
                        output_encoded = Strings.encode(output.array())
                        result['data'][abi] = output_encoded
                        result['error'] = None
                    except:
                        result['error'] = "encoding function call data failed"
        else:
            result['error'] = "type \"{}\" not supported for format \"\"".format(input_type, __name__)

    return result

def decode(arguments = None):
    result = {}
    result['error'] = 'decoding failed'
    result['data'] = {}
    args = _parse_args_for_codec(arguments)

    if not args['error']:
        input_type, abi, input_data = args['data']
        input_data = input_data[PREFIX_LENGTH:] if input_data[:PREFIX_LENGTH] == HEX_PREFIX else input_data
        signatures = {}
        signatures['error'] = 'signature invalid'

        if type:
            if input_type == TYPE_TX:
                # TODO: implement
                pass
            elif input_type == TYPE_DATA:
                input_data_with_signature = None

                if abi:
                    # abi was provided by user
                    try:
                        abi = abi.strip()
                        signature = Function(abi).selectorHex()
                        signatures['data'] = [abi]
                        signatures['error'] = None
                        input_data_with_signature = "{}{}".format(signature.strip(), input_data)
                    except:
                        result['error'] = "signature invalid"
                else:
                    # abi not provided, look it up
                    hex_signature = input_data[:HEX_SIGNTURE_LENGTH].strip()
                    signatures = _lookup_function_signatures("{}{}".format(HEX_PREFIX, hex_signature))
                    input_data_with_signature = input_data.strip()

                if not signatures['error']:
                    result['error'] = 'decoding failed'
                    result['data'] = {}

                    for signature in signatures['data']:
                        # com.esaulpaugh.headlong.abi.Function.decodeCall(hexdata) returns a Java tuple
                        # casting to python list makes the tuple mutable
                        result_raw = None
                        function_name = Function.parse(signature)
                        
                        try:
                            result_raw = list(function_name.decodeCall(FastHex.decode(input_data_with_signature)))
                        except:
                            result['error'] = 'decoding failed'

                        if result_raw:
                            decoded = _parse_params_for_decode(result_raw)
                            result['data'][signature] = "({})".format(simplejson.dumps(decoded)[1:-1])
                            result['error'] = None
                else:
                    result['error'] = signatures['error']
            else:
                result['error'] = "[-] type \"{}\" not supported for format \"\"".format(input_type, __name__)
    else:
        result['error'] = args['error']
    
    return result

def _parse_params_for_encode(input_data):
    result = []

    for param in input_data:
        result.append(_parse_param_for_encode(param))

    return result

def _parse_param_for_encode(input_data):
    result = None

    if type(input_data).__name__ == 'list':
        result = _parse_params_for_encode(input_data)
    else:
        try:
            int(input_data)
            result = hex(input_data)[2:]

            if result[len(result) - 1] == 'L':
                result = result[:-1]
            if len(result) % 2:
                # pad if odd
                result = "0{}".format(result)
        except:
            identifier = input_data[:2]
            
            if identifier == HEX_PREFIX:
                # it's an address
                result = input_data[2:].lower()
            elif identifier == "s'":
                # it's a string
                result = input_data[2:-1]
                data_bytes = bytearray(result, 'utf-8')
                result = ''.join('{:02x}'.format(x) for x in data_bytes).lower()
            elif identifier == "b'":
                # it's bytes
                result = input_data[2:-1].lower()
                
                if len(result) % 2:
                    # pad if odd
                    result = "0{}".format(result)
            else:
                print("[-] unknown param type, skipping ", input_data)
    return result

# parse a Java iterable to Python
def _parse_params_for_decode(parameters):
    result = []
    
    for parameter in parameters:
        result.append(_parse_param_for_decode(parameter))

    return result

# parse abi-decoded input recursively
def _parse_param_for_decode(parameter):
    result = None

    # if the parameter is iterable
    if type(parameter).__name__.lower() in JAVA_ITERABLES_LOWERCASE:
        try:
            if parameter.typecode == 'b':
                # it's an array of bytes
                # convert Java int8 bytes to Python uint8
                # courtesy of stackoverflow
                parameter = ''.join('{:02x}'.format(array_element & 0xff) for array_element in parameter)
                result = parameter
            else:
                # it's an another type of array
                result = _parse_params_for_decode(parameter)
        except:
            # it's a tuple
            result = _parse_params_for_decode(parameter)
    else:
        try:
            # check if the parameter is an Ethereum address
            if len(hex(parameter)) == HEX_ADDRESS_LENGTH:
                result = hex(parameter)[:-1]
            # otherwise leave it as is
            else:
                result = parameter    
        except:
            result = parameter

    return result

def _parse_args_for_codec(arguments = None):
    result = {}
    result['error'] = 'abi or input data invalid'
    result['data'] = None

    if type(arguments).__name__ == 'dict':
        input_type = arguments['type'] if 'type' in arguments and  _validate_argument(arguments['type']) else None
        abi = arguments['abi'] if 'abi' in arguments and  _validate_argument(arguments['abi'])  else None
        input_data = arguments['input'] if 'input' in arguments and  _validate_argument(arguments['input']) else None
        result['data'] = input_type, abi, input_data
        result['error'] = None
    else:
        result['data'] = "abi or input data invalid"
    
    return result

def _validate_argument(argument = None):
    return argument and len(argument)

def _lookup_function_signatures(hex_signature = None):
    result = {}
    result['error'] = 'signature invalid'
    result['data'] = None

    if hex_signature and len(hex_signature) == HEX_SIGNTURE_LENGTH + PREFIX_LENGTH:
        try:
            params = {}
            params[API_GET_PARAM_HEX_SIGNATURE] = hex_signature
            params = urllib.urlencode(params)
            url = "{}{}?{}".format(API_URL, API_ENDPOINT_SIGNATURES, params)
            response = urllib.urlopen(url,).read()

            try:
                response_data = simplejson.loads(response)
                
                if response_data['count'] > 0:
                    result['error'] = None
                    result['data'] = [element['text_signature'] for element in response_data['results']]
                else:
                    result['error'] = "no matches found for signature {}".format(hex_signature)
            except Exception as error:
                result['error'] = str(error)
        except Exception as error:
            result['error'] = str(error)
    # else:
    #     result['error'] = 'signature invalid'

    return result