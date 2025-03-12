class CourseSerializer:
    def __init__(self, instance, many=False):
        self.instance = instance
        self.many = many

    def to_dict(self):
        if self.many:
            return [self._serialize_object(obj) for obj in self.instance]
        return self._serialize_object(self.instance)

    def _serialize_object(self, obj):
        return {
            "id": obj.id,
            "name": obj.name,
            "description": obj.description,
            "created_at": obj.created_at.isoformat() if obj.created_at else None,
            "updated_at": obj.updated_at.isoformat() if obj.updated_at else None,
        }
