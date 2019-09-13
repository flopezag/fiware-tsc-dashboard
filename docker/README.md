# Supported tags and respective `Dockerfile` links

-	[`latest`, `2.2.0`](https://github.com/flopezag/fiware-tsc-dashboard/docker/Dockerfile)

# Quick reference

-	**Where to get help**:  
	[the Docker Community Forums](https://forums.docker.com/), [the Docker Community Slack](https://blog.docker.com/2016/11/introducing-docker-community-directory-docker-community-slack/), or [Stack Overflow](https://stackoverflow.com/search?tab=newest&q=docker)

-	**Where to file issues**:  
	[https://github.com/flopezag/fiware-tsc-dashboard/issues](https://github.com/flopezag/fiware-tsc-dashboard/issues)

-	**Maintained by**:  
	[the FIWARE Foundation Operative Office](https://github.com/flopezag)

-	**Image updates**:  
	[official-images PRs](https://github.com/flopezag/fiware-tsc-dashboard/pulls?q=is%3Apr+is%3Aclosed)  
	[official-images repo's `fiware-tsc-dashboard` file](https://github.com/flopezag/fiware-tsc-dashboard/...) ([history](https://github.com/flopezag/fiware-tsc-dashboard/...))

-	**Source of this description**:  
	[docs repo's `fiware-tsc-dashboard/` directory](https://github.com/flopez/fiware-tsc-dashboard/docker/tree/master) ([history](https://github.com/flopez/fiware-tsc-dashboard/docker/commits/master))

# What is FIWARE Generic Enablers Dashboard Server?

This README will guide you through running the FIWARE Generic Enablers Dashboard Server with Docker Containers. This 
script was developed in order to get information of the community in terms of evolution and use of the different
FIWARE Generic Enablers with the purpose of catching the pulse of the FIWARE Ecosystem on the full, incubated, 
supported, and deprecated FIWARE Generic Enablers.

It is important to keep in mind that this service requests huge amount of queries toward Github, therefore it is normal
that sometimes, even providing the corresponding Github credentials, the number of requests exceed the hour limit 
(5.000 requests/hour). The service is prepared on that cases and wait one hour in order to recover the request limit
per hour.

# QuickStart with FIWARE Generic Enablers Dashboard Server and Docker

Here is how to get a FIWARE Generic Enablers Dashboard Server running on Docker containers:

**Step - 1 :** Make a copy of the example [configuration file](https://github.com/flopezag/fiware-tsc-dashboard/blob/develop/config/tsc-dashboard.ini) 
and complete the information. Keep in mind that the docker compose use this local file to mount a volume in order to 
proper configure the server.

**Step - 2 :** Due to this service will access a google sheet to put the current execution data, it is needed to 
configure the proper service credentials, your google account credentials and google spreadsheet credentials 
in Google.

**Step - 3 :** Run FIWARE Generic Enablers Dashboard docker container through Docker Compose

`docker-compose up`

# Creation of docker images

In order to create the corresponding docker image, you can execute the command:

```console
docker build --rm --build-arg -t docker-enabler-dashboard .
```

It will create the corresponding image based on the last version of master. Nevertheless if you want to create a image
based on other branch, you can specify the BRANCH argument variable during the creation process with the following
command:

```console
docker build --rm --build-arg BRANCH=develop -t docker-enabler-dashboard .
```


# License

Jira Management Script Server is licensed under APACHE License 2.0


