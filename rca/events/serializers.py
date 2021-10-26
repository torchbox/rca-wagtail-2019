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


class RelatedSchoolSerializer(Field):
    def to_representation(self, value):
        schools = []
        for school in value.all():
            schools.append(
                {
                    "id": school.id,
                    "page": {
                        "id": school.page.id,
                        "meta": {"detail_url": school.page.full_url},
                        "title": school.page.title,
                        "intranet_slug": school.page.intranet_slug,
                    },
                }
            ),
        return schools
