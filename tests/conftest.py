import datetime as dt

import pytest
from django.core import management
from django_scopes import scopes_disabled

from pretalx.event.models import Event, Organiser, Team
from pretalx.person.models import User
from pretalx.schedule.models import Room
from pretalx.submission.models import Submission, SubmissionStates, SubmissionType


@pytest.fixture(scope="session", autouse=True)
def collect_static(request):
    management.call_command("collectstatic", "--noinput", "--clear")


@pytest.fixture
def organiser():
    with scopes_disabled():
        o = Organiser.objects.create(name="Super Organiser", slug="superorganiser")
        Team.objects.create(
            name="Organisers",
            organiser=o,
            can_create_events=True,
            can_change_teams=True,
            can_change_organiser_settings=True,
            can_change_event_settings=True,
            can_change_submissions=True,
        )
        Team.objects.create(name="Reviewers", organiser=o, is_reviewer=True)
    return o


@pytest.fixture
def event(organiser):
    today = dt.date.today()
    with scopes_disabled():
        event = Event.objects.create(
            name="Fancy testevent",
            is_public=True,
            slug="test",
            email="orga@orga.org",
            date_from=today,
            date_to=today + dt.timedelta(days=3),
            organiser=organiser,
        )
        event.enable_plugin("pretalx_media_ccc_de")
        event.save()
        for team in organiser.teams.all():
            team.limit_events.add(event)
    return event


@pytest.fixture
def orga_user(event):
    with scopes_disabled():
        user = User.objects.create_user(
            password="orgapassw0rd",
            email="orgauser@orga.org",
            name="Orga User",
        )
        team = event.organiser.teams.filter(
            can_change_organiser_settings=True, is_reviewer=False
        ).first()
        team.members.add(user)
        team.save()
    return user


@pytest.fixture
def review_user(event):
    with scopes_disabled():
        user = User.objects.create_user(
            password="reviewpassw0rd",
            email="reviewuser@orga.org",
            name="Review User",
        )
        team = event.organiser.teams.filter(
            can_change_organiser_settings=False, is_reviewer=True
        ).first()
        team.members.add(user)
        team.save()
    return user


@pytest.fixture
def orga_client(orga_user, client):
    client.force_login(orga_user)
    return client


@pytest.fixture
def review_client(review_user, client):
    client.force_login(review_user)
    return client


@pytest.fixture
def submission(event):
    with scopes_disabled():
        sub_type = SubmissionType.objects.create(
            name="Talk", event=event, default_duration=30
        )
        sub = Submission.objects.create(
            title="Test Talk",
            event=event,
            code="TSTALK",
            submission_type=sub_type,
        )
    return sub


@pytest.fixture
def room(event):
    with scopes_disabled():
        return Room.objects.create(name="Main Room", event=event)


@pytest.fixture
def schedule_with_talk(event, submission, room):
    with scopes_disabled():
        submission.state = SubmissionStates.CONFIRMED
        submission.save()
        schedule = event.wip_schedule
        schedule.talks.create(
            submission=submission,
            room=room,
            start=dt.datetime.combine(event.date_from, dt.time(10, 0), tzinfo=dt.UTC),
            end=dt.datetime.combine(event.date_from, dt.time(10, 30), tzinfo=dt.UTC),
            is_visible=True,
        )
        schedule = event.wip_schedule.freeze("v1")[0]
    return schedule
