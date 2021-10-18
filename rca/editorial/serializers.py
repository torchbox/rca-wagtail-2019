from rest_framework.fields import Field


class EditorialTypeTaxonomySerializer(Field):
    def to_representation(self, value):
        return [{"title": v.type.title, "id": v.type.id} for v in value.all()]


class RelatedAuthorSerializer(Field):
    def to_representation(self, value):
        return {"name": value.name, "id": value.id}
