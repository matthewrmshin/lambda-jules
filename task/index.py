"""Wrap JULES to run under in the AWS Lambda Python 3.7 Runtime.

Input: `event['body']` is expected to contain base64 encoded bytes that decode
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


def handler(event: dict, context) -> dict:
    """Handle the lambda call.

    Create and change into a temporary directory.
    Unpack the input there.
    Invoke JULES.
    Pack the output and return.
    """
    # Run in a temporary location to guarantee writable
    tempdir = TemporaryDirectory()
    os.chdir(tempdir.name)
    os.makedirs('output')
    unpack_input(event)
    # Set up executable and shared library path
    mybin = os.path.join(os.path.dirname(__file__), 'bin', 'jules.exe')
    try:
        run([mybin], check=True)
        return {
            'statusCode': 200,
            'body': pack_output(),
            'headers': {'content-type': 'application/octet-stream'},
            'isBase64Encoded': True,
        }
    finally:
        os.chdir('/var/task')
        tempdir.cleanup()


def unpack_input(event: dict) -> None:
    """Unpack the input bytes in `event['body']` into the current directory.

    `event['body']` is expected to contain base64 encoded bytes that decode
    into a tar-gzip file containing the essential input files to JULES,
    including namelists, ancilliary files and forcing files. The tar-gzip
    archive should have all files in a flat directory at the root level. The
    output directory setting in the `output.nml` should be set to `./output`.
    """
    with tarfile.open(fileobj=BytesIO(b64decode(event['body']))) as handle:
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
