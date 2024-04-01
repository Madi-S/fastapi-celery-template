import requests
from unittest import mock
from fastapi.testclient import TestClient

from project.users.models import User
from project.users import users_router, tasks
from project.users.factories import UserFactory


def test_pytest_setup(client: TestClient, db_session):
    # test view
    response = client.get(users_router.url_path_for('form_example_get'))
    assert response.status_code == 200

    # test db
    user = User(username='test', email='test@example.com')
    db_session.add(user)
    db_session.commit()
    assert user.id


def test_view_with_eager_mode(client, db_session, settings, monkeypatch):
    mock_requests_post = mock.MagicMock()
    monkeypatch.setattr(requests, 'post', mock_requests_post)

    monkeypatch.setattr(
        settings,
        'CELERY_TASK_ALWAYS_EAGER',
        True,
        raising=False
    )

    user_name = 'michaelyin'
    user_email = f'{user_name}@accordbox.com'
    response = client.post(
        users_router.url_path_for('user_subscription'),
        json={'email': user_email, 'username': user_name},
    )
    assert response.status_code == 200
    assert response.json() == {
        'message': 'successfully sent task to Celery',
    }

    mock_requests_post.assert_called_with(
        'https://httpbin.org/delay/5',
        data={'email': user_email}
    )


def test_user_subscribtion_view(client, db_session, settings, monkeypatch, user_factory):
    user = user_factory.build()

    task_add_subscription = mock.MagicMock(name='task_add_subscription')
    task_add_subscription.return_value = mock.MagicMock(task_id='task_id')
    monkeypatch.setattr(tasks.task_add_subscription,
                        'delay', task_add_subscription)

    response = client.post(
        users_router.url_path_for('user_subscription'),
        json={'email': user.email, 'username': user.username}
    )

    assert response.status_code == 200
    assert response.json() == {
        'message': 'successfully sent task to Celery',
    }

    # query from the db again
    user = db_session.query(User).filter_by(username=user.username).first()
    task_add_subscription.assert_called_with(user.id)
