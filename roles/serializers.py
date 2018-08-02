from rest_framework import serializers
from roles.models import BodyRole
from roles.models import InstituteRole
from roles.models import PERMISSION_CHOICES
from roles.models import INSTITUTE_PERMISSION_CHOICES
from bodies.serializer_min import BodySerializerMin
from users.serializers import UserProfileSerializer
from events.serializers import EventSerializer
from events.prioritizer import get_r_fresh_prioritized_events

class RoleSerializer(serializers.ModelSerializer):
    """Role Serializer"""

    permissions = serializers.MultipleChoiceField(choices=PERMISSION_CHOICES)
    body_detail = BodySerializerMin(read_only=True, source='body')
    users_detail = UserProfileSerializer(many=True, read_only=True, source='users')
    bodies = serializers.SerializerMethodField()

    class Meta:
        model = BodyRole
        fields = ('id', 'name', 'inheritable', 'body', 'body_detail', 'bodies',
                  'permissions', 'users', 'users_detail', 'priority')

    @classmethod
    def get_bodies(cls, obj):
        """Gets bodies including children if inheritable."""
        if not obj.inheritable:
            return BodySerializerMin([obj.body], many=True).data
        return BodySerializerMin(cls.get_children_recursive(obj.body, []), many=True).data

    @classmethod
    def get_children_recursive(cls, body, children):
        """Returns an array including a body and its children."""
        for child_body_relation in body.children.all():
            cls.get_children_recursive(child_body_relation.child, children)
        children.append(body)
        return children

class RoleSerializerWithEvents(serializers.ModelSerializer):
    """Role Serializer with nested events of bodies"""

    permissions = serializers.MultipleChoiceField(choices=PERMISSION_CHOICES)
    events = serializers.SerializerMethodField()
    body_detail = BodySerializerMin(read_only=True, source='body')
    bodies = serializers.SerializerMethodField()
    get_bodies = lambda self, obj: RoleSerializer.get_bodies(obj)

    class Meta:
        model = BodyRole
        fields = ('id', 'name', 'inheritable', 'body', 'body_detail',
                  'bodies', 'permissions', 'events', 'priority')

    def get_events(self, obj):
        return EventSerializer(get_r_fresh_prioritized_events(
            obj.body.events.all(), self.context['request']), many=True).data

class RoleSerializerMin(serializers.ModelSerializer):

    users_detail = UserProfileSerializer(many=True, read_only=True, source='users')

    class Meta:
        model = BodyRole
        fields = ('id', 'name', 'body', 'users_detail', 'priority')

class RoleSerializerMinAlt(serializers.ModelSerializer):
    """Alternative min serializer for BodyRole"""

    body_detail = BodySerializerMin(read_only=True, source='body')

    class Meta:
        model = BodyRole
        fields = ('id', 'name', 'body_detail', 'priority')

class InstituteRoleSerializer(serializers.ModelSerializer):

    permissions = serializers.MultipleChoiceField(choices=INSTITUTE_PERMISSION_CHOICES)

    class Meta:
        model = InstituteRole
        fields = ('id', 'name', 'permissions')
