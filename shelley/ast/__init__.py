actions = []
events = []
components = []


def find_instance_by_name(name: str, instances):
    instance = None
    try:
        instance = [instance for instance in instances if instance.name == name][0]
    except IndexError:
        pass

    return instance
