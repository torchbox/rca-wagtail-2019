from rest_framework.fields import Field


class EventTaxonomySerializer(Field):
    def to_representation(self, value):
        return {"title": value.title, "id": value.id}


class RelatedDirectoratesSerializer(Field):
    def to_representation(self, value):
        return [
            {"title": v.directorate.title, "id": v.directorate.id}
            for v in value.filter(directorate__isnull=False)
        ]
