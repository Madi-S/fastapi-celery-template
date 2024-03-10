# Fastapi Celery Template

```bash
git clone https://github.com/Madi-S/fastapi-celery-template
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
