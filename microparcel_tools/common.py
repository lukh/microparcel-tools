class FieldEnum(object):
    def __init__(self, name, enumerators):
        self.name = name
        self.enumerators = enumerators

    @property
    def bitsize(self):
        l = len(self.enumerators) - 1
        bs = 0
        while l > 0:
            bs += 1
            l = l >> 1
        bs = bs if bs > 0 else 1
        return bs

    def __repr__(self):
        return "ENUM({})<{}>: [{}]".format(self.name, self.bitsize, ", ".join(self.enumerators))

class Field(object):
    def __init__(self, name, short_name, offset=None, bitsize=None, enumerators=None, enum=None):
        self.name = name
        self.short_name = short_name
        
        self.offset = offset

        if enum is not None:
            self.enum = enum
            self.bitsize = enum.bitsize

        elif enumerators is not None:
            self.enum = FieldEnum(name, enumerators)
            self.bitsize = self.enum.bitsize

        else:
            self.enum = None
            self.bitsize = bitsize

        if self.bitsize > 16:
            raise ValueError()

    @property
    def field_type(self):
        if self.enum is None:
            return "uint{}_t".format(8 if self.bitsize <= 8 else 16)
        else:
            return self.enum.name

    def __repr__(self):
        return "{} | {} ({}): off={}, size={}".format(self.name, self.short_name, self.field_type, self.offset, self.bitsize)

class Node(object):
    def __init__(self, subcat=None, children=None, fields=None, senders=None):
        assert (isinstance(subcat, Field) or subcat is None)
        assert (children is None or all([isinstance(c, Node) for c in children]))
        assert (fields is None or all([isinstance(f, Field) for f in fields]))
        
        self.parent = None
        self.subcat = subcat

        self.children = children if children is not None else []

        self.fields = fields if fields is not None else []

        self.senders = senders if senders is not None else []



