"""Run JULES on upload event on input S3 bucket.

This Lambda is expected to trigger on upload to the input S3 bucket.
The handler will:
* Create temporary directory, and change current working directory to it.
* Download and extract the input object to current working directory.
  * Expect TAR-GZIP archive containing input files for a simple JULES run.
* Run JULES.
* TAR-GZIP content of current working directory and upload to output S3 bucket.
* Delete input object from input bucket.
"""
from contextlib import suppress
from io import BytesIO
import logging
import os
from subprocess import run, STDOUT
import tarfile
from tempfile import gettempdir, TemporaryDirectory


import boto3


JULES_EXE = os.path.join(os.path.dirname(__file__), 'bin', 'jules.exe')
S3 = boto3.resource('s3')


def handler(event: dict, _):
    """Run Jules.

    Create and change into a temporary directory.
    Download and extract input configuration from input S3 bucket.
    Run JULES.
    Pack output and upload to output S3 bucket.
    Delete input object from input S3 bucket.
    """
    # Run in a temporary location to guarantee writable
    origdir = gettempdir()
    with suppress(OSError):
        origdir = os.getcwd()
    for record in event['Records']:
        tempdir = TemporaryDirectory()
        os.chdir(tempdir.name)
        try:
            load_config(record)
            run(
                [os.getenv('JULES_EXE', JULES_EXE)],
                check=True,
                stdout=open(os.path.basename(JULES_EXE) + '.log', 'wb'),
                stderr=STDOUT,
            )
        except Exception as exc:
            logging.warning(record)
            logging.exception(exc)
        finally:
            save_result(record)
            tidy_config(record)
            os.chdir(origdir)  # Make sure we are no longer in tempdir
            tempdir.cleanup()


def load_config(record: dict) -> None:
    """Read event record, load and extract config from input S3 bucket.

    Args:
        record: Record of S3 upload event.
    """
    bio = BytesIO()
    _input_s3_object(record).download_fileobj(bio)
    bio.seek(0, 0)
    with tarfile.open(fileobj=bio) as handle:
        handle.extractall()


def save_result(record: dict) -> None:
    """Save the result of a JULES run to the output S3 bucket.

    Args:
        record: Record of S3 upload event.
    """
    bio = BytesIO()
    with tarfile.open(fileobj=bio, mode='w:gz') as handle:
        for name in sorted(os.listdir()):
            handle.add(name, recursive=True)
    bio.seek(0, 0)
    S3.Object(
        os.getenv('OUTPUT_BUCKET'),
        record['s3']['object']['key'],
    ).upload_fileobj(bio)


def tidy_config(record: dict) -> None:
    """Remove the input object from the input S3 bucket."""
    _input_s3_object(record).delete()


def _input_s3_object(record: dict):
    """Return the S3 object resource for the bucket object in record."""
    return S3.Object(
        record['s3']['bucket']['name'],
        record['s3']['object']['key'],
    )
