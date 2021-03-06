import uuid

from django.conf import settings
from django.test import TestCase

from api.tests.factories import UserFactory
from core.models import AllocationSource
from core.models import EventTable


# TODO:
# - Multiple allocation_source_created events for the same source_id
# - Multiple allocation_source_created events for the same name
# - Invalid compute_allowed (-1, '5000', NaN)
# - Use Hypothesis to generate
#
# - allocation_source_deactivated event
#   - What happens to a user who has this as an allocation source
#   - What happens to an instance running with this as a source
#
# - allocation_source_updated
#   - What happens if the compute used changed
#   - What happens if you try to change the source_id
#   - What happens if you try to update a source which doesn't exist
from core.models import UserAllocationSource


class CyVerseAllocationTests(TestCase):
    def setUp(self):
        if 'cyverse_allocation' not in settings.INSTALLED_APPS:
            self.skipTest('CyVerse Allocation plugin is not enabled')

    def test_allocation_source_created(self):
        new_allocation_source = {
            'source_id': str(uuid.uuid4()),
            'name': 'TestAllocationSourceCreateScenario',
            'compute_allowed': 50000
        }

        # Make sure no allocation_source_created event for this source exists
        event_count_before = EventTable.objects.filter(
            name='allocation_source_created',
            payload__name='TestAllocationSourceCreateScenario'
        ).count()
        self.assertEqual(event_count_before, 0)

        # Make sure that no Allocation Source with our test source name exists
        allocation_source_count_before = AllocationSource.objects.filter(
            name=new_allocation_source['name']).count()
        self.assertEqual(allocation_source_count_before, 0)

        allocation_source_count_before = AllocationSource.objects.filter(
            source_id=new_allocation_source['source_id']).count()
        self.assertEqual(allocation_source_count_before, 0)

        # Add an event 'allocation_source_created' with our test source name
        new_event = EventTable.create_event(name='allocation_source_created',
                                            payload=new_allocation_source,
                                            entity_id=new_allocation_source['source_id'])

        # Make sure we added the event successfully
        event_count_after = EventTable.objects.filter(
            name='allocation_source_created',
            payload__name='TestAllocationSourceCreateScenario'
        ).count()
        self.assertEqual(event_count_after, 1)

        # Make sure that there is now an Allocation Source with the test name
        allocation_source_count_after = AllocationSource.objects.filter(
            source_id=new_allocation_source['source_id'],
            name=new_allocation_source['name']).count()
        self.assertEqual(allocation_source_count_after, 1)

        allocation_source = AllocationSource.objects.filter(
            source_id=new_allocation_source['source_id'],
            name=new_allocation_source['name']).first()
        self.assertEqual(allocation_source.compute_allowed, new_allocation_source['compute_allowed'])

    def test_user_allocation_source_assigned(self):
        new_allocation_source = {
            'source_id': str(uuid.uuid4()),
            'name': 'TestAllocationSourceAssociateScenario',
            'compute_allowed': 50000
        }
        new_event = EventTable.create_event(name='allocation_source_created',
                                            payload=new_allocation_source,
                                            entity_id=new_allocation_source['source_id'])
        user = UserFactory.create()
        new_user_allocation_source = {
            'source_id': new_allocation_source['source_id'],
            'username': user.username
        }

        # Make sure no allocation_source_assigned event for this user and source exists
        event_count_before = EventTable.objects.filter(
            name='user_allocation_source_assigned',
            payload__username=user.username,
            payload__source_id=new_user_allocation_source['source_id']
        ).count()
        self.assertEqual(event_count_before, 0)

        # Make sure that no Allocation Source and User combination exists
        user_allocation_source_count_before = UserAllocationSource.objects.filter(
            allocation_source__source_id=new_user_allocation_source['source_id'],
            user=user).count()
        self.assertEqual(user_allocation_source_count_before, 0)

        # Add an event 'allocation_source_created' with our test source name
        new_event = EventTable.create_event(name='user_allocation_source_assigned',
                                            payload=new_user_allocation_source,
                                            entity_id=new_user_allocation_source['username'])

        # Make sure we added the event successfully
        event_count_after = EventTable.objects.filter(
            name='user_allocation_source_assigned',
            payload__username=user.username,
            payload__source_id=new_user_allocation_source['source_id']
        ).count()
        self.assertEqual(event_count_after, 1)

        # Make sure that there is now an Allocation Source with the test name
        user_allocation_source_count_after = UserAllocationSource.objects.filter(
            allocation_source__source_id=new_user_allocation_source['source_id'],
            user=user).count()
        self.assertEqual(user_allocation_source_count_after, 1)

        user_allocation_source = UserAllocationSource.objects.filter(
            allocation_source__source_id=new_user_allocation_source['source_id'],
            user=user).first()
        self.assertEqual(user_allocation_source.allocation_source.compute_allowed,
                         new_allocation_source['compute_allowed'])
        self.assertEqual(user_allocation_source.allocation_source.source_id, new_allocation_source['source_id'])
        self.assertEqual(user_allocation_source.allocation_source.name, new_allocation_source['name'])
