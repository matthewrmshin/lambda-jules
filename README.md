<p>
  <a href="https://github.com/matthewrmshin/lambda-jules/actions"><img alt="GitHub Actions status" src="https://github.com/matthewrmshin/lambda-jules/workflows/Python%20application/badge.svg"></a>
  <a href="https://github.com/matthewrmshin/lambda-jules/actions"><img alt="GitHub Actions status" src="https://github.com/matthewrmshin/lambda-jules/workflows/Lint%20misc%20files/badge.svg"></a>
</p>

# What is this?

This project documents how to build and deploy JULES as an AWS Lambda.

![S3->Lambda->S3](./images/S3-Lambda-S3.svg)

The template contains:
* A S3 *Configuration* Bucket.
  * Expect each uploaded object to be TAR-GZIP archive.
  * Each TAR-GZIP archive contains input namelists and forcing files for JULES
    at the root level.
  * Triggers the Lambda when an object is uploaded.
* A S3 *Output* Bucket.
  * Each output object will be a TAR-GZIP archive.
  * Each TAR-GZIP archive contains all the input files + output files of a run.
  * STDOUT and STDERR from JULES are sent to `jules.exe.log`, so available for
    inspection as part of an output archive.
* A Lambda that runs a Python wrapper to:
  * Read events from the Configuration Bucket.
  * Download the input object from the Configuration Bucket and extract content.
  * Run JULES with the extracted input files.
  * Archive output and upload to the Output Bucket.
  * Delete the input object from the Configuration Bucket.

## How to Deploy

You need an environment that has:
* AWS CLI and cfn-lint utilities.
* Enough access to create resources in your AWS account via the AWS CLI.
* Docker.

(I use an EC2 instance.)

You will also need a copy of JULES vn5.6 or above. Copy or symbolic link the
JULES source tree to under `jules_source/` of this project or
`export JULES_SOURCE` to point to the location of the JULES source tree.

To deploy, run `./me deploy stf-jules-dev`.

When the stack is no longer required, run `./me destroy stf-jules.dev`.

## What's Next?

Convert to SAM template.
Set up build and deployment in AWS CodePipeline.
