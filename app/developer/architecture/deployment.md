# Deployment

Where each part runs. Checked against the backend's `deployment/` folder and the repositories' workflows on 28 November 2026; what is not recorded in a repository is marked as such.

## The backend: AWS, described in Terraform

`backend/deployment/terraform` describes a deployment in the `ap-southeast-1` region, with its state in an S3 bucket:

- a **VPC** with public and private subnets, and security groups for the load balancer, the API instances and the database (`vpc.tf`);
- the **API servers**: an EC2 launch template, an auto-scaling group and an application load balancer (`ec2.tf`);
- the **database**: an RDS instance, with its password generated and kept in Secrets Manager (`rds.tf`, `sm.tf`);
- the **grader**: an AWS Lambda function named `<env>-cadet-grader`, with handler `index.runAll`, 512 MB of memory and a configurable timeout (`lambda.tf`). The file sets the runtime `nodejs12.x`; whether production uses a newer runtime is not recorded here, and the grader's current needs should be compared with it;
- two existing **S3 buckets** (assets and configuration) that the file looks up (`s3.tf`), and an IoT policy for remote execution on devices (`iot.tf`).

An API server runs the backend as a **release**: the workflow `cd.yml` builds it with `mix release` and publishes it as the GitHub release `latest-deploy`; `deployment/init.sh` downloads that tarball and installs the systemd service `cadet.service` (it also serves as the manual deployment guide for any Linux server with systemd).

## Static sites: GitHub Pages

Most of the rest is static files on GitHub Pages, each built by its own repository's workflow:

- the **directories** (`language-directory`, `plugin-directory`, and the plugin directory file of `plugins`) and the **modules** (`modules`);
- the **evaluators** (js-slang, py-slang, scm-slang, java-slang, ocaml-slang) and the **plugin bundles** (`plugins`);
- the playground-only build of the **frontend**, at <https://source-academy.github.io>;
- the documentation sites: <https://docs.sourceacademy.org> (this repository publishes into the deployment repository `docs.sourceacademy.org`, as js-slang and py-slang do) and <https://about.sourceacademy.org> (the `about` repository).

## The full frontend

The build with login and assessments, for Source Academy @ NUS and for other institutions, is configured by environment variables at build time (the backend's address, the directory URLs, and so on; see [Frontend](./frontend)). Where it is hosted is not recorded in the frontend repository.

## Running your own

The README of the frontend covers a local playground and a local Source Academy @ NUS; the backend README covers a local backend and the manual deployment on a Linux server. A complete guide to a deployment of one's own ("Source Academy @ X") is in the `about` repository, [`deployment`](https://github.com/source-academy/about/tree/master/deployment).
