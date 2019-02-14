# PHOTOMOSAIC STACK

Everything you need to run your own local photomosaic cluster.

## Prerequisites

Docker is required to start the cluster, if you don't have it installed get it [here](https://docs.docker.com/) 

To create each photomosaic let's go severless. We make use of [OpenFaaS](https://docs.openfaas.com/) an open source Function as a Service project as the name implies. You will need to install the [faas-cli](https://github.com/openfaas/faas-cli/). 
The hands on workshop you can find there will walk you through all the steps to set things up but if you just want a curl command

```bash
curl -sSL https://cli.openfaas.com | sudo sh
```
or with homebrew on Mac

```bash
brew install faas-cli
```

## Setting up the environment
Next we need to configure the required environment variables for this project

It is highly recommended you use a tool [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) to create a virtual environment.

If you use virtualenvwrapper create a new environment like

```bash
mkvirtualenv mosaic-stack-example
Using base prefix '/usr'
New python executable in /home/username/.virtualenvs/mosaic-stack-example/bin/python3
Also creating executable in /home/username/.virtualenvs/mosaic-stack-example/bin/python
Installing setuptools, pip, wheel...done.
virtualenvwrapper.user_scripts creating /home/username/.virtualenvs/mosaic-stack-example/bin/predeactivate
virtualenvwrapper.user_scripts creating /home/username/.virtualenvs/mosaic-stack-example/bin/postdeactivate
virtualenvwrapper.user_scripts creating /home/username/.virtualenvs/mosaic-stack-example/bin/preactivate
virtualenvwrapper.user_scripts creating /home/username/.virtualenvs/mosaic-stack-example/bin/postactivate
virtualenvwrapper.user_scripts creating /home/username/.virtualenvs/mosaic-stack-example/bin/get_env_details
(mosaic-stack-example) username@some-machine:~/STACK/photomosaic_open_faas$ 
```
now add the following to your `~/.virtualenvs/mosaic-stack-example/bin/postactivate`

If you've forgone using a virtualenv you can put in `~/.bashrc`

```bash
export PROJECT_PATH={PATH_TO_THIS_DIRECTORY}
export BROADCAST_IP={IP_ADDRESS_OF_YOUR_MACHINE}
export SECRET_KEY={GENERATE_A_RANDOM_STRING}
export S3_ENDPOINT_URL='http://localstack-s3:4572/'
export S3_EXTERNAL_URL="http://${BROADCAST_IP}:4572"
export MAIL_PASSWORD={GMAIL_ACCOUNT_PASSWORD TO SEND NOTIFICATIONS}
export MAIL_USERNAME={GMAIL_ACCOUNT_USERNAME DONT USE YOUR REAL ONE}
export AWS_SECRET_KEY='' # an empty string if using localstack  
export AWS_ACCESS_KEY_ID='' # an empty string if using localstack
export MEDIA_BUCKET='images'
export FRONT_END_URL="http://${BROADCAST_IP}:8081"
export FAAS_URL='http://faas-swarm:8080'
export MOSAIC_API_URL='http://mosaic-api:5000/api/v1/photomosaic'
export MONGODB_URI='mongodb://mongodb:27017/'
export PYTHONPATH=.:$PROJECT_PATH

alias awsl=awslocal
alias home='cd $PROJECT_PATH'
home

function make_bucket() { awsl s3 mb s3://$@ && awsl s3api put-bucket-acl --bucket $@ --acl public-read;}

```

with that done you are almost ready to bring up the stack
install the awscli with 

`pip3 install -r requirements.txt`

Next start the docker swarm with 

`docker swarm init`

It may tell you that you need to choose an advertise address, copy the ip address it displays
and enter

`docker swarm init --advertise-addr={THE_IP_ADDRESS_IT_SHOWED}`

Then run the setup script with `bash run_stack.sh`

You should see the following output

```bash
Updating service func_mosaic-api (id: 150n39zg1wkr2wsg8twnkkwjb)
Updating service func_localstack-s3 (id: 4eo0x3y8livaudjkc51o1bq7k)
Updating service func_mongodb (id: m88h9r7goxacd3ce910p4hm1w)
Updating service func_gateway (id: r18yt7ylbjxvm5lkqalbl4wpb)
Updating service func_faas-swarm (id: kh4uew1hbx1vxmuyh5zlmlbql)
Updating service func_nats (id: t58bvg24nfvyschyt64syzcd7)
Updating service func_queue-worker (id: mcvq34mnzlvjl2ta0vk4gj3fk)
The counter is 0
HTTP/1.1 200 OK
 the website is working fine
Deploying: mosaic-healthcheck.

Deployed. 202 Accepted.
URL: http://127.0.0.1:8080/function/mosaic-healthcheck

Deploying: mosaic-maker.

Deployed. 202 Accepted.
URL: http://127.0.0.1:8080/function/mosaic-maker

```

Navigate to `http://localhost:5000/` and you should see the swagger documentation
The OpenFaas UI should also be available at `http://localhost:8080`

Check all the services are deployed by using the command `docker service ls`

If everything deployed correctly you should see

```bash
ID                  NAME                 MODE                REPLICAS            IMAGE                                       PORTS
kh4uew1hbx1v        func_faas-swarm      replicated          1/1                 openfaas/faas-swarm:0.6.1                   
r18yt7ylbjxv        func_gateway         replicated          1/1                 openfaas/gateway:0.9.14                     *:8080->8080/tcp
4eo0x3y8liva        func_localstack-s3   replicated          1/1                 localstack/localstack:latest                *:4572->4572/tcp
m88h9r7goxac        func_mongodb         replicated          1/1                 bitnami/mongodb:latest                      *:27018->27017/tcp
150n39zg1wkr        func_mosaic-api      replicated          1/1                 ryanjvanvoorhis/mosaic-api:latest           *:5000->5000/tcp
t58bvg24nfvy        func_nats            replicated          1/1                 nats-streaming:0.11.2                       
mcvq34mnzlvj        func_queue-worker    replicated          1/1                 openfaas/queue-worker:0.5.4                 
2q6lrosnx3a3        mosaic-healthcheck   replicated          1/1                 ryanjvanvoorhis/mosaic-healthcheck:latest   
wu3tybu78jho        mosaic-maker         replicated          1/1                 ryanjvanvoorhis/mosaic-maker:latest    
```

If everything is up then it's time to spin up the ui

Clone the repository and continue from there

`git clone https://github.com/rjvanvoorhis/photomosaic-fe-v2.git`

## License
[MIT](https://choosealicense.com/licenses/mit/)
