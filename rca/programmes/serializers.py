from rest_framework import serializers
from rest_framework.fields import Field

from rca.programmes.models import DegreeLevel


class DegreeLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DegreeLevel
        fields = ("id", "title")


class RelatedSubjectSerializer(Field):
    def to_representation(self, value):
        for v in value.all():
            subjects = []
            for v in value.all():
                subject = {}
                subject["id"] = v.subject.id
                subject["title"] = v.subject.title
                subject["description"] = v.subject.description
                subjects.append(subject)
        return subjects


class RelatedSchoolSerializer(Field):
    def to_representation(self, value):
        for v in value.all():
            schools = []
            for v in value.all():
                school = {}
                school["id"] = v.page.id
                school["title"] = v.page.title
                schools.append(school)
        return schools
