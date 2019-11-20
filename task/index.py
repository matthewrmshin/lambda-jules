"""Run JULES using an AWS Lambda Python 3.7 Runtime.

Input: The request body is expected to contain base64 encoded bytes that decode
into a tar-gzip file containing the essential input files to JULES, including
namelists, ancilliary files and forcing files. The tar-gzip archive should have
all files in a flat directory at the root level. The output directory setting
in the `output.nml` should be set to `./output`.

Output: The response body will contain base64 encoded bytes that decode into a
tar-gzip file containing the output files in a flat directory at the root
level.
"""


from base64 import b64decode, b64encode
from io import BytesIO
import os
from subprocess import run
import tarfile
from tempfile import TemporaryDirectory


def handler(event: dict, _) -> dict:
    """Handle the lambda call."""
    http_method = event.get('httpMethod')
    if http_method == 'POST':
        return {
            'statusCode': 200,
            'body': run_jules(event),
            'headers': {'content-type': 'application/octet-stream'},
            'isBase64Encoded': True,
        }
    elif http_method == 'GET':
        return {
            'statusCode': 200,
            'body': __doc__,
        }
    else:
        return {
            'statusCode': 405,
            'body': f'{http_method} not supported',
        }


def run_jules(event: dict) -> dict:
    """Run Jules.

    Create and change into a temporary directory.
    Unpack the input there.
    Invoke JULES.
    Pack the output and return.
    """
    # Run in a temporary location to guarantee writable
    tempdir = TemporaryDirectory()
    os.chdir(tempdir.name)
    os.makedirs('output')
    unpack_input(event['body'])
    # Set up executable and shared library path
    mybin = os.path.join(os.path.dirname(__file__), 'bin', 'jules.exe')
    try:
        run([mybin], check=True)
        return pack_output()
    finally:
        os.chdir('/var/task')
        tempdir.cleanup()


def unpack_input(body: str) -> None:
    """Unpack the input bytes in `body` into the current directory.

    `body` is expected to contain base64 encoded bytes that decode into a
    tar-gzip file containing the essential input files to JULES, including
    namelists, ancilliary files and forcing files. The tar-gzip archive should
    have all files in a flat directory at the root level. The output directory
    setting in the `output.nml` should be set to `./output`.
    """
    with tarfile.open(fileobj=BytesIO(b64decode(body))) as handle:
        handle.extractall()


def pack_output() -> str:
    """Pack the content of the output directory.

    :return: The response body will contain a string that is a base64 encoded
    bytes that can be decoded into a tar-gzip file containing the output files
    in a flat directory at the root level.
    """
    ret = BytesIO()
    with tarfile.open(fileobj=ret, mode='w:gz') as handle:
        for name in os.listdir('output'):
            handle.add(os.path.join('output', name), name)
    return b64encode(ret.getvalue()).decode()
