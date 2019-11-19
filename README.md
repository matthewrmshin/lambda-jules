<p>
  <a href="https://github.com/matthewrmshin/myawsdocs/actions"><img alt="GitHub Actions status" src="https://github.com/matthewrmshin/myawsdocs/workflows/Python%20application/badge.svg"></a>
</p>

# What is this?

This project documents how to build and deploy JULES as an AWS Lambda.

## Building Fortran executable for AWS Lambda

Current efforts documented in these projects:
* [lambda-gfortran-fcm-make-netcdf](https://github.com/matthewrmshin/lambda-gfortran-fcm-make-netcdf)
  Dockerfile based on AWS Lambda Python 3.7 runtime environment,
  with GFortran, FCM Make and netCDF libraries.

Note: To use the docker image. You will need to be in an environment that can run
[Docker](https://www.docker.com/). The easiest way is to use an Amazon EC2
instance by following the instructions:
* [Setting Up with Amazon EC2](https://docs.aws.amazon.com/en_pv/AWSEC2/latest/UserGuide/get-set-up-for-amazon-ec2.html)
* [Getting Started with Amazon EC2 Linux Instances](https://docs.aws.amazon.com/en_pv/AWSEC2/latest/UserGuide/EC2_GetStarted.html)
* [Docker Basics for Amazon ECS](https://docs.aws.amazon.com/en_pv/AmazonECS/latest/developerguide/docker-basics.html)

## Building the Lambda Package

1. Get JULES, export a suitable source tree from
   [MOSRS](https://code.metoffice.gov.uk/). (Account required.)
   a. Run `svn pget fcm:revision https://code.metoffice.gov.uk/svn/jules/main`
      to find out the revision numbers of release versions or just go for trunk@HEAD.
   b. Run, for example, `svn export https://code.metoffice.gov.uk/svn/jules/main/trunk@15927 jules-5.6`
      to get a source tree for vn5.6.
2. Make sure you have write access to the current working directory.
3. Clone this project. E.g. `git clone https://github.com/matthewrmshin/lambda-jules.git`.
4. Run `./lambda-jules/bin/build-lambda-jules /path/to/jules` where
   `/path/to/jules` is the path to the JULES source tree you exported from
   MOSRS in step 1.
5. The lambda package will be written to `./lambda-jules.zip`.

## Deploying the Lambda Package

1. After building the package, run `./lambda-jules/bin/deploy-lambda-jules`.

## How to Create an Input Package for the Lambda

For now... Choose a suitable [Rose](https://github.com/metomi/rose/) application configuration
with JULES input. Inspect the `rose-app.conf`. Set:
* Any location based variables to `.`. Note current locations of these input files.
* Search for other environment variables substitution syntax. Make sure they are resolved.
* Create a new directory elsewhere and change directory to it.
  E.g. `mkdir /var/tmp/jules-sample-inputs; cd /var/tmp/jules-sample-inputs`.
* Run `rose app-run -C $OLDPWD true`.
* Make sure all other input files are copied in.
* Set output directory to `./output`.
* Tar-gzip the content so that the input files are all under the root location
  in the archive.

## What's Next?

Set up tests in AWS CodePipeline.
