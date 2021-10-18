from rest_framework.fields import Field


class EventTaxonomySerializer(Field):
    def to_representation(self, value):
        return {"title": value.title, "id": value.id}


class RelatedDirectoratesSerializer(Field):
    def __init__(self, related_model=None, *args, **kwargs):
        super().__init__()
        self.related_model = related_model

    def to_representation(self, value):
        return [
            {"title": v.directorate.title, "id": v.directorate.id} for v in value.all()
        ]
