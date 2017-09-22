from rest_framework import serializers
from communication.models import Communication, CommunicationRelation, Message, PhoneCall, Fax, Letter
import heritage
import development


class CommunicationTypeSerializer(serializers.ModelSerializer):
    '''
    Does nothing yet.
    '''
    pass


class LetterSerializer(CommunicationTypeSerializer):
    class Meta:
        model = Letter


class FaxSerializer(CommunicationTypeSerializer):
    class Meta:
        model = Fax


class PhoneCallSerializer(CommunicationTypeSerializer):
    class Meta:
        model = PhoneCall


class MessageSerializer(CommunicationTypeSerializer):
    class Meta:
        model = Message


class CommunicationTypeObjectRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        """
        Serialize related communication type object instances using their respective serializers.
        """
        if isinstance(value, Message):
            serializer = MessageSerializer(value)
        elif isinstance(value, PhoneCall):
            serializer = PhoneCallSerializer(value)
        elif isinstance(value, Fax):
            serializer = FaxSerializer(value)
        elif isinstance(value, Letter):
            serializer = LetterSerializer(value)
        else:
            raise Exception('Unexpected type of communication object')
        return serializer.data


class CedarObjectCommunicationRelatedField(serializers.RelatedField):
    def to_representation(self, instance):
        """
        Serialize cedar object instances related to comm objects using their respective serializers.
        Any model instance that is expected to be attached to comms needs to define
        a get_default_serializer_class() method that returns the serializer
        needed for that model.
        """
        # if isinstance(instance, development.models.DevelopmentProject):
        #     serializer = development.serializers.DevelopmentProjectSerializer(instance)
        # elif isinstance(instance, heritage.models.HeritageProject):
        #     serializer = heritage.serializers.ProjectSerializer(instance)
        # else:
        #     raise Exception('Unexpected type of communication object')

        serializer = instance.get_default_serializer_class()(instance)
        return serializer.data


class CommunicationRelationSerializer(serializers.ModelSerializer):
    comm_type = CommunicationTypeObjectRelatedField(read_only=True, source='comm.comm_type')

    # comm_type_model = serializers.CharField(source='comm.comm_type_ct.model', read_only=True)

    class Meta:
        model = CommunicationRelation
