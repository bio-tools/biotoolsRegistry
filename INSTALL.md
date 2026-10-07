## Installing bio.tools on your system
The local (development) installation is done via [Docker](https://www.docker.com/). Other than Git (and a text editor), nothing else is required to run and write code for bio.tools. Production deployments use a separate [compose.prod.yml](compose.prod.yml) file — see **step 5**.

## 1. Download and Install Docker
##### Docker main installation page
[https://docs.docker.com/install/](https://docs.docker.com/install/)
> **Note:** You will need to create a [Docker Hub](https://hub.docker.com) account.

##### Windows
[https://docs.docker.com/docker-for-windows/install/](https://docs.docker.com/docker-for-windows/install/)

> Read the "What to know before you install" information to see if Docker Destktop for Windows can be installed on your system.  If your system does not meet the requirements to run Docker Desktop for Windows, you can install the legacy [Docker Toolbox](https://docs.docker.com/toolbox/overview/).

##### MacOS
[https://docs.docker.com/docker-for-mac/install/](https://docs.docker.com/docker-for-mac/install/)

##### CentOS
[https://docs.docker.com/install/linux/docker-ce/centos/](https://docs.docker.com/install/linux/docker-ce/centos/)

##### Debian
[https://docs.docker.com/install/linux/docker-ce/debian/](https://docs.docker.com/install/linux/docker-ce/debian/)

##### Fedora
[https://docs.docker.com/install/linux/docker-ce/fedora/](https://docs.docker.com/install/linux/docker-ce/fedora/)

##### Ubuntu
[https://docs.docker.com/install/linux/docker-ce/ubuntu/](https://docs.docker.com/install/linux/docker-ce/ubuntu/)

## 2. Clone the repo
##### Using HTTPS
`git clone https://github.com/bio-tools/biotoolsRegistry.git`

##### Using SSH
`git clone git@github.com:bio-tools/biotoolsRegistry.git`

Go into the folder in which you cloned the bio.tools repo. By default it will be called `biotoolsRegistry`: (e.g. `cd biotoolsRegistry ` or `cd /home/user/coding/biotoolsRegistry`)

## 3. Configure environment variables

The Docker setup reads configuration from a `.env` file in the repository root. A template is provided in `.env.example`:

```sh
cp .env.example .env
```

Then edit `.env` and adjust the values as needed:

* `BIOTOOLS_*` — Django application settings (database connection, Elasticsearch URL, email, ORCID, secret key, etc.)
* `MYSQL_*` — credentials for the MySQL **container itself**. These should match the `BIOTOOLS_MYSQL_*` values above (e.g. `MYSQL_USER` must equal `BIOTOOLS_MYSQL_USER`).
* `GITHUB_TOKEN`, `HUGGINGFACE_TOKEN` — tokens used by the metadata bridge service.

Notes for each setup:

* **Development (`compose.yml`)**: the defaults from `.env.example` work out of the box. Emails are printed to the backend container console (`BIOTOOLS_EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`), so no SMTP credentials are needed.
* **Production (`compose.prod.yml`)**: all values are required. You **must** set:
  * `BIOTOOLS_SECRET_KEY` (a long random string; never use the example value)
  * `BIOTOOLS_DEBUG=False`
  * `BIOTOOLS_DEPLOYMENT=prod`
  * `BIOTOOLS_URL_FRONT` — the public URL of your instance
  * `BIOTOOLS_EMAIL_*` — real SMTP credentials (bio.tools production uses [Zoho mail](http://zoho.com))
  * `BIOTOOLS_ORCID_*` — ORCID client credentials and callback URL
  * `MYSQL_ROOT_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD` — matching the `BIOTOOLS_MYSQL_*` values

> **Note:** `.env` is git-ignored. Never commit it or share its contents.

## 4. Development setup (docker compose)
The development setup uses [compose.yml](compose.yml), which is meant for local development and testing only. It *must not* be used for production deployment. All `docker compose` commands in this section should be run from the root folder of the Git project (e.g. `biotoolsRegistry`) and use `compose.yml` by default.

## 4.0 Inside the bio.tools repo
> **Note:** The Docker setup will require up to 5 GB of disk space. The bio.tools data will also add to this.

##### 4.0.1 Build the necessary Docker images
`docker compose build`

The above command will download / build all the Docker images required for bio.tools to run on your local machine. 

The images built can be seen by running: `docker image ls` and are:

* `biotools/frontend` `(~ 827MB)`
* `biotools/backend` `(~ 1.12GB)`
* `mysql` `(~ 205MB)` (will show up after running **4.0.2**)
* `elasticsearch` `(~ 486MB)` (will show up after running **4.0.2**)
* `python` `(~ 925MB)`
* `node` `(~ 650MB)`

##### 4.0.2 Create and run the Docker containers
`docker compose up`

The above command will create and run the required containers:

* `biotools-mysql`
* `biotools-elasticsearch`
* `biotools-backend` (depends on `biotools-mysql` and `biotools-elasticsearch`)
* `biotools-frontend`(depends on `biotools-backend`)
* `biotools-caddy`

> **Note:** After running the `docker compose up` command, the containers will start and will output log messages which you can see in your terminal window. In order for the containers to keep running this window needs to stay open. You will need to open new terminal windows/tabs for other operations.

> `docker compose up` will also build the images if they do not exist, but in order to be sure your latest source code and image changes are running make sure you run `docker compose build` beforehand

Too see the running containers run: `docker container ls` or `docker ps`

## 4.1 The short(er) setup
**Run the steps below in the root folder of the Git project (e.g. `biotoolsRegistry`)** 

##### 4.1.1 Make migrations
`docker exec biotools-backend python manage.py makemigrations`

Make Django migrations from the exiting models. Executed on the `biotools-backend` container. If you get the `No changes detected` message it means that you are up to date.

##### 4.1.2 Migrate to the DB
`docker exec biotools-backend python manage.py migrate`

Create necessary tables and other DB objects from the migrations. Executed on the `biotools-backend` container. If you get the `No migrations to apply.` message it means that you are up to date. 

##### 4.1.3 Copy initial (seed) DB
`docker cp initial_db.sql biotools-mysql:/root`

Copies the `initial_db.sql` SQL file into the `biotools-mysql` container (where the MySQL database server runs) into the `/root` folder.


##### 4.1.4 Copy initial DB load script file
`docker cp load_initial_db.sh biotools-mysql:/root`

Copies the `load_initial_db.sh` into the `biotools-mysql` container. This file will run the MySQL commands used to load the database described in `initial_db.sql`

##### 4.1.5 Execute initial DB load script file
`docker exec biotools-mysql bash /root/load_initial_db.sh`

Executes the `load_initial_db.sh` file in the `biotools-mysql` container which loads the initial (seed) DB data.

> **Note:** The initial DB contains 6 tool annotations, a superuser (username: `biotools`, password: `biotools`), an initial `test` subdomain and the necessary EDAM files. See 4.1.8 for more.


##### 4.1.6 Purge Elasticsearch
`docker exec biotools-backend python manage.py es_purge`

Purges (clears) any data in the Elasticsearch index. Executed in the `biotools-backend` container which communicates with the `biotools-elasticsearch` container.

##### 4.1.7 Regenerate Elasticsearch
`docker exec biotools-backend python manage.py es_regenerate`

Takes all the tools, subdomains annotations etc. in the DB  and creates the equivalent entries in the Elasticsearch index. Executed in the `biotools-backend` container.

##### 4.1.8 Done
At this point you can go to [http://localhost](http://localhost]) to see the local bio.tools homepage.

The `test` subdomain can be viewed at [http://localhost/t?domain=test](http://localhost/t?domain=test)


You can login with the existing superuser (user: `biotools`, password: `biotools`).

All running Docker containers can be stopped by running: `docker compose down` from the root Git folder. This will preserve the data in the MySQL database and Elasticsearch. To reinstantiate everything again run: `docker compose up`. 

Only need to run `docker compose build` once at the beginning or if changes are made to the bio.tools Docker settings files.

If you wish to remove the data along with the containers run: `docker compose down -v` which will also remove the Docker volumes which preserve the MySQL and Elasticsearch data.



## 4.2 The longer setup
This is an alternative to **4.1** in which some of the steps were contained in the initial DB files. This will start with no data.

**Run the steps below in the root folder of the Git project (e.g. `biotoolsRegistry`)** 

##### 4.2.1 Make migrations
`docker exec biotools-backend python manage.py makemigrations`

Make Django migrations from the exiting models. Executed on the `biotools-backend` container.

##### 4.2.2 Migrate to the DB
`docker exec biotools-backend python manage.py migrate`

Create necessary tables and other DB objects from the migrations. Executed on the `biotools-backend` container.

##### 4.2.3 Create a superuser
`docker exec -it biotools-backend python manage.py createsuperuser`

Prompts the creation of a superuser, need to input superuser name, email (optional) and password. Executed on the `biotools-backend` container.


##### 4.2.4 Setup EDAM ontology
`docker exec biotools-backend bash /elixir/application/backend/data/edam/update_edam.sh`

Download EDAM ontology and push it to the DB. Can also be used to update to new EDAM version. The file which indicates the EDAM version is `<git_project_root>/backend/data/edam/current_version.txt`, e.g. `biotoolsRegistry/backend/data/edam/current_version.txt`


##### 4.2.5 Copy helper tables SQL
`docker cp update_site_settings.sql biotools-mysql:/root`

Copies the `update_site_settings.sql ` SQL file into the `biotools-mysql` container (where the MySQL database server runs) into the `/root` folder. This file contains SQL instructions used to create helper tables and settings for the project.

##### 4.2.6 Copy script file to run helper tables
`docker cp update_site_settings.sh biotools-mysql:/root`

Copies the `update_site_settings.sh ` into the `biotools-mysql` container. This file will run the MySQL commands described in `update_site_settings.sql`

##### 4.2.7 Execute script file
`docker exec biotools-mysql bash /root/update_site_settings.sh`

Executes the `update_site_settings.sh ` file in the `biotools-mysql` container which loads the helper tables and settings in the DB.

##### 4.2.8 Purge Elasticsearch
`docker exec biotools-backend python manage.py es_purge`

Purges (clears) any data in the Elasticsearch index. Executed in the `biotools-backend` container which communicates with the `biotools-elasticsearch` container.

##### 4.2.9 Regenerate Elasticsearch
`docker exec biotools-backend python manage.py es_regenerate`

Takes all the tools, subdomains annotations etc. in the DB  and creates the equivalent entries in the Elasticsearch index. Executed in the `biotools-backend` container.

##### 4.2.10 Grant test privileges
`docker exec -i biotools-mysql mysql -u root -pelixirroot -e "GRANT ALL PRIVILEGES ON *.* TO 'elixir'@'%' WITH GRANT OPTION; FLUSH PRIVILEGES;"`

Fixes `Access denied for user 'elixir'@'%' to database 'test_elixir'"` errors when running tests with `docker exec biotools-backend python manage.py test`.

If it complains that the `elixir_test` database exists, run this command: `docker exec -i biotools-mysql mysql -u root -pelixirroot -e "DROP DATABASE test_elixir;"`

##### 4.2.11 Done
At this point you can go to [http://localhost](http://localhost) to see the local bio.tools homepage.

Login with the user created in **4.2.3**

No tools or subdomains are available, add tools at [http://localhost/register]([http://localhost/register]) and subdomains at [http://localhost/subdomain](http://localhost/subdomain)

All running Docker containers can be stopped by running: `docker compose down` from the root Git folder. This will preserve the data in the MySQL database and Elasticsearch. To reinstantiate everything again run: `docker compose up`.

Only need to run `docker compose build` once at the beginning or if changes are made to the bio.tools Docker settings files.

If you wish to remove the data along with the containers run: `docker compose down -v` which will also remove the Docker volumes which preserve the MySQL and Elasticsearch data.


## 5. Production setup (docker compose -f compose.prod.yml)
The production setup uses [compose.prod.yml](compose.prod.yml) together with the root [Dockerfile](Dockerfile). It builds a self-contained application image (backend + frontend served by Caddy) and additionally runs a task runner and a rendertron service.

**Run the commands below from the root folder of the Git project.**

### 5.0.1 Configure environment variables
Follow **step 3** and create a complete `.env` file. All values are required in production, in particular `BIOTOOLS_SECRET_KEY`, `BIOTOOLS_DEBUG=False`, `BIOTOOLS_DEPLOYMENT=prod`, `BIOTOOLS_URL_FRONT`, the SMTP (`BIOTOOLS_EMAIL_*`) and ORCID (`BIOTOOLS_ORCID_*`) settings, and the `MYSQL_*` credentials matching the `BIOTOOLS_MYSQL_*` values.

The `biotools` and `taskrunner` services load the full `.env` file via `env_file`, while the `mysql` service reads the `MYSQL_*` variables.

### 5.0.2 Build and start the containers
```sh
docker compose -f compose.prod.yml up --build -d
```

This creates and runs:

* `biotools-mysql` (MySQL database)
* `biotools-elasticsearch` (Elasticsearch search engine)
* `biotools-registry` (the bio.tools application, served on port 80)
* `biotools-taskrunner` (processes background tasks via `python manage.py process_tasks`)
* `biotools-metadata-bridge` (metadata bridge, uses `GITHUB_TOKEN` / `HUGGINGFACE_TOKEN`)
* `biotools-rendertron` (rendering service on port 3000)

### 5.0.3 Initialize the database
On first start, run migrations and load initial data as needed:

```sh
docker exec biotools-registry python manage.py migrate
docker exec biotools-registry python manage.py es_regenerate
```

### 5.0.4 Stopping and updating
```sh
docker compose -f compose.prod.yml down          # stop (keeps data in volumes)
docker compose -f compose.prod.yml down -v       # stop and remove data volumes
docker compose -f compose.prod.yml up --build -d # rebuild and start after pulling changes
```


## 6. Useful information
### 6.0 Basic usage (development)
After completing steps 1-4 above, the only required commands for basic use are

`docker compose up`

and

`docker compose down`

and perhaps

`docker compose down -v`

### 6.1 Local dev
After running `docker compose up` you will see a number of log messages. These messages come from the running containers:

* `biotools-mysql` (MySQL logs)
* `biotools-elasticsearch` (Elasticsearch logs)
* `biotools-backend` (Mostly Apache logs, sometimes Python logs)
* `biotools-frontend` (Gulp logs)

#### 6.1.1 Backend dev
The `biotools-backend` container is based on an image which uses an Apache server. The logs from `biotools-backend` come from Apache or sometimes from Python. 

> **Note:** Changes in Python/Django/backend files will be reflected in the `biotools-backend` container, **BUT** because of how Apache works, the changes won't be reflected in your browser http://localhost until Apache is reloaded. In order to see the changes in the reflected in the browser you need to run: 
> 
> `docker exec biotools-backend /etc/init.d/apache2 reload`

> **Remember** to run the above command whenever you want to see your code changes reflected in your local bio.tools.

> Bringing the containers down and up again will also work, but this takes significantly longer. The above command is almost instant.

Most issues with the backend code will be reflected in the browser at http://localhost/api/{some_path}, e.g. [http://localhost/api/tool](http://localhost/api/tool) or [http://localhost/api/jaspar](http://localhost/api/jaspar) etc. 

See [https://biotools.readthedocs.io/en/latest/api_reference.html](https://biotools.readthedocs.io/en/latest/api_reference.html) or Django route files (`urls.py`) for more API endpoints.

#### 6.1.2 Frontend dev
The `biotools-frontend` container outputs logs from **`gulp`** ([https://gulpjs.com/](https://gulpjs.com/)) which bundles all frontend JavaScript and CSS code. 

Every time you change and save a `.js` or `.css` file in the frontend, gulp will re-bundle everything automatically. This implies that all changes in the frontend are reflected automatically in thr browser, unlike for the backend.

> **Note:** If you have a syntax error in your JavaScript or CSS files, gulp will fail and you won't see any changes reflected in the browser. So, if your changes are not reflected, look at the `biotools-frontend` logs of gulp which will indicate if you made a syntax error in your code.

### 6.2 Update EDAM

Similarly to section **4.2.4**, in order to update to the latest EDAM version (or just use a different EDAM version) the `update_edam.sh` needs to be executed on the `biotools-backend` container.

The version number used for updating EDAM is specified in the file:
`<git_project_root>/backend/data/edam/current_version.txt`

In order to update to the latest EDAM version (e.g. `1.23`) edit the `current_version.txt` file to store the value `1.23`, save the file and run:

`docker exec biotools-backend bash /elixir/application/backend/data/edam/update_edam.sh`

The script file will download the specific EDAM version .owl file from [https://github.com/edamontology/edamontology](https://github.com/edamontology/edamontology) and execute the:

`python /elixi/application/manage.py parse_edam` 

command in the `biotools-backend` container.

> **Note:** The `current_version.txt` file is tracked by Git and any changes involving EDAM versions other than latest should not be pushed to the main branches of the repo.

### 6.3 Local email setup
Email settings are configured via environment variables in the `.env` file (see step 3). In development, the default `BIOTOOLS_EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` prints emails to the `biotools-backend` container console instead of sending them.

In order for the emails to actually be sent you need to provide credentials (email, password, smtp settings) in `.env` via the `BIOTOOLS_EMAIL_*` variables. bio.tools production uses Zoho mail (http://zoho.com) which currently works well with our setup.

The easy way would be to make a Zoho email account and use that email information to make the email functionality run. Gmail and Yahoo were tried and the connections are blocked by Gmail and Yahoo because of security reasons. This is because Gmail and Yahoo don't accept a simple username-password login and require more strict settings. Feel free to implement this in your bio.tools instance.


### 6.4 Docker notes

#### Build bio.tools Docker images (dev)
`docker compose build`

#### Run bio.tools containers (dev)
`docker compose up`

#### Stop bio.tools containers
`docker compose down`

#### Stop bio.tools containers and remove data
`docker compose down -v`

#### View running containers
`docker container ls`
`docker ps`

#### View all containers
`docker container ls -a`

#### Remove stopped containers
`docker container rm <CONTAINER_ID>`

or 

`docker container rm <CONTAINER_ID1> <CONTAINER_ID2> <CONTAINER_ID3>`


#### Force remove containers
`docker container rm -f <CONTAINER_ID>`

or 

`docker container rm -f <CONTAINER_ID1> <CONTAINER_ID2> <CONTAINER_ID3>`

#### Prune containers (Remove all stopped containers)
`docker container prune`

#### View images 
`docker image ls`

#### Remove image
`docker image rm <IMAGE_ID>`

or

`docker image rm <IMAGE_ID1> <IMAGE_ID2> <IMAGE_ID2>`

(will not work if containers are running this image)


#### Enter a container and run commands
Any of the bio.tools runnning containers can provide a bash terminal to run commands inside the containers (similar to `docker exec`). Examples of the commands are:

* `docker exec -it biotools-mysql bash`
* `docker exec -it biotools-elasticsearch bash`
* `docker exec -it biotools-backend bash`
* `docker exec -it biotools-frontend bash`

As an example, to view the info in a MySQL database table run:

1. `docker exec -it biotools-mysql bash`
2. In container: `mysql -u elixir -p` (password is by default 123)
3. In MySQL: 

`use elixir;`

`SELECT * FROM elixir_resource WHERE visibility = 1;`


#### bio.tools Docker settings files:

Backend build config file

* `<git_project_root>/backend/Dockerfile.dev` (development)

Frontend build config file

* `<git_project_root>/frontend/Dockerfile.dev` (development)

Backend dockerignore file

* `<git_project_root>/backend/.dockerignore`

docker-compose YAML config files

* `<git_project_root>/compose.yml` (development)
* `<git_project_root>/compose.prod.yml` (production)
* `<git_project_root>/Dockerfile` (production build of the full application)

Environment variables

* `<git_project_root>/.env.example` — template; copy to `.env` and edit (see step 3)


#### Docker documentation:
* [https://docs.docker.com/](https://docs.docker.com/)
* [https://docs.docker.com/reference/](https://docs.docker.com/reference/)
* [https://docs.docker.com/engine/reference/commandline/container/](https://docs.docker.com/engine/reference/commandline/container/)
* [https://docs.docker.com/engine/reference/commandline/image/](https://docs.docker.com/engine/reference/commandline/image/)
* [https://docs.docker.com/config/pruning/](https://docs.docker.com/config/pruning/)
* [https://docs.docker.com/compose/](https://docs.docker.com/compose/)
* [https://hub.docker.com/](https://hub.docker.com/)
