def get_diff(old, new):
    old_data = {}
    new_data = {}

    for field in old._meta.fields:
        name = field.name
        if name in ("id", "created_at", "updated_at"):
            continue

        old_val = getattr(old, name)
        new_val = getattr(new, name)

        if old_val != new_val:
            old_data[name] = str(old_val)
            new_data[name] = str(new_val)

    if not old_data:
        return None

    return {"old": old_data, "new": new_data}


def serialize_instance(instance):
    return {
        field.name: str(getattr(instance, field.name))
        for field in instance._meta.fields
    }
