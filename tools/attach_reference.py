from objects.reference import Reference

def attach_reference(elements):
    result = []
    pending_reference = None

    for i, el in enumerate(elements):
        if isinstance(el, Reference):
            pending_reference = el
        else:
            if pending_reference:
                setattr(el, 'reference', pending_reference)
                pending_reference = None
            result.append(el)

    return result
