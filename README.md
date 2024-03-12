# Fastapi Celery Template

```bash
$ git clone https://github.com/Madi-S/fastapi-celery-template
```

## Why Celery?

Celery is an open source, asynchronous task queue that is often coupled with Python-based web frameworks like FastAPI, Django or Flask to manage background work outside the typical request/response cycle In other words, you can return an HTTP response back immediately and run the process as a background task instead of forcing the user to wait for the task to be finished.

Potential use cases:

1. You have developed a messaging app that provides "@ mention" functionality where a user can reference another user via `@<username>` in a comment. The mentioned user receives an email notification. This is probably fine to handle synchronously for a single mention, but if one user mentions ten users in a single comment, you will need to send then different emails. Since you will probably have to talk to an external service, you may run into network issues. Regardless, this is a task that you will want to run in the background.

2. If your messaging app allows a user to upload a profile image, you will probably want to use a background process to generate a thumbnail.

As you build out you web app, you should try to ensure that the response time of a particular view is lower than 500ms. Application Performance Monitoring tools like "New Relic" or "Scout" can be used to help surface potential issues and isolate longer process that could be moved in a background process managed by Celery.

## Celery vs FastAPI's BackgroundTasks

It is worth noting that you can leverage FastAPI's BackgroundTasks class, which comes directly from Starlette, to run tasks in the background.

For example:

```python
from fastapi import BackgroundTasks

def send_email(email, message):
    ...

@app.get('/')
async def ping(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, 'email@test.com', 'Hello World')
    return {'ping': 'pong'}
```

So when should you use Celery instead of BackgroundTasks?

1. CPU intensive tasks: Celery should be used for tasks that perform heavy background computations since BackgroundTasks runs in the same event loop that serves you app's requests.

2. Task queue: If you require a task queue to manage the tasks and workers, you should probably use Celery. Often you will want to retrieve the status of a job and then perform some action based on the status - i.e., send an error email, kick off a different background task, or retry the task. Celery manages this all for you.

## Celery vs RQ vs Huey

RQ (Redis Queue) and Huey are other open source, Python-based task-queues that are often compared to Celery. While the core logic of Celery, RQ and Huey are very much the same in thath they all use the producer/consumer model, they differ in that:

1. Both RQ and Huey are much simpler to use and easier to learn than Celery. However, both lack some features and can only be used with Redis.

2. Celery is quite a bit more complex and harder to implement and learn, but it is much more flexible and has many more features. It supports Redis along with a number of other backends.

## Message Broker and Result Backend

Let's start with some terminology:

-   Message broker is an intermediary program used as the transport for producing or consuming tasks.
-   Result backend is used to store the result of a Celery task.

The Celery client is the producer, which adds a new task to the queue via the message broker. Celery workers then consume new tasks from the queue, again, via the message broker. Once processed, results are then stored in the result backend.

In terms of tools, RabbitMQ is arguably the better choice for a message broker since it supports AMQP (Advanced Message Queuing Protocol) while Redis is fine as your result backend.

# Gettings Started

## Setting up Redis

You can set up and run Redis directly from your operating system or from a Docker container.

### With Dcoker

To download the official Redis Docker image from Docker Hub and run it on port 6379 in background:

```bash
$ docker run -p 6379:6379 --name some-redis -d redis
```

To test if Redis is up and running:

```bash
$ docker exec -it some-redis redis-cli ping

PONG
```

### Without Docker

Either download Redis from source or via package manager (like apt, yum, homebrew or chocolately) and then start the Redis server via:

```bash
$ redis-server
```

## Setting up Celery

![Celery Workflow](static/celery_workflow.png)

## Sending a Task to Celery

After activating virtual environment and installing all the `requirements.txt` dependencies, we can run the following command:

```bash
(venv)$ cd project
(venv)$ celery -A main.celery worker --loglevel=info
```

You should see something similar to this:

```bash
[config]
    .> app: main:0x10ad0d5f8
    .> transport: redis://127.0.0.1:6379/0
    .> results: redis://127.0.0.1:6379/0
    .> concurrency: 8 (prefork)
    .> task events: OFF (enable -E to monitor tasks in this worker)

[queues]
.> celery exchange=celery(direct) key=celery

[tasks]
    . main.divide
```

Now let's send some tasks to Celery worker:

```python
from main import app, divide

task = divide.delay(1, 2)
```

What's happenning?

1. We used the `delay` method to send a new message to the message broker. The worker process then picked up and executed the task from the queue.
2. After releasing from the Enter key, the code finished executing while the `divide` task ran in the background.

```python
task = divide.delay(1, 2)

print(type(task))
>>> '<class.result.AsyncResult>'
```

After we called the delay method, we get an `AsyncResult` instance, which can be used to check the task state along with the return value or exception details.

Add a new task then print `task.state` and `task.result`, we should get something like `PENDING None` at first, but after some time we should see `SUCCESS 0.5`

But what happens if there is an error?

```python
task = divide.delay(1, 0)

print(task.state, task.result)
>>> 'FAILURE' ZeroDivisionError('division by zero')
```

## Monitoring Celery with Flower

Flower is a real-time web applciation monitoring and administrating tool for Celery.

We can spin up the Flower server by:

```bash
(venv)$ celery -A main.celery flower --port=5555
```

And if we go to `localhost:5555`, we will see a Flower dashboard, where we can get much of feedback about Celery tasks.

# Application Factory

## Some Useful Commands

To intialize alembeic:

```bash
(venv)$ alembic init alembic
```

To create an empty sqlite3:

```bash
(venv)$ python

>>> from main import app
>>> from project.database import Base, engine
>>> Base.metadata.create_all(bind=engine)
>>> exit()

(venv)ls db.sqlite3
db.sqlite3
```

## Definitions

-   `main.py` - uses `create_app` to create a fastapi app

-   `project/__init__.py` - factory function

-   `project/config.py` - fastapi config

-   `project/users` - relevant models and routes for `Users`

## Migrations

```bash
(venv)$ alembic revision --autogenerate
(venv)$ alembic upgrade head
```

## Celery Tasks

Many resources recommend using `celery.task` decorator. This might cause circular imports since you will have to import the Celery instance. We used `celery.shared_task` to make our code reusable, which again, requires `current_app` in `create_celery` instead of creating a new Celery instance. Now, we can copy this file in the app and it will work as expected.

# Dockerizing Application

Why should we serve up our development environment in Docker containers with Docker Compose?

1. Instead of having to run each process (e.g, Uvicorn/FastAPI, Celery worker, Celery beat, Flower, Redis, Postgres, etc) manually, each from a different terminal window, after we containerize each service, Docker Compose enables us to manage and run the containers using a single command.

2. Docker Compose will also simplify configuration. The Celery config is currently tied to our FastAPI app's config. This is not ideal. With Docker Compose, we can easily create different configurations for both FastAPI and Celery all from a single YAML file.

3. Docker, in general, allows us to create isolated, reproducible, and portable environments. So, you will not have to mess around with a virtual environment or install tools like Postgres and Redis on your local OS.

Our `docker-compose.yml` file defines 6 services:

-   `web` is the FastAPI server
-   `db` is the Postgres server
-   `redis` is the Redis service, which will be used as the Celery message broker and result backend
-   `celery_worker` is the Celery worker process
-   `celery_beat` is the Celery beat process for scheduled tasks
-   `flower` is the Celery dashboard
