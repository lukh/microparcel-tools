class FieldEnum(object):
    def __init__(self, name, enumerators):
        self.name = name
        self.enumerators = enumerators

    @property
    def named_enumerators(self):
        for e in self.enumerators:
            yield self.name + "_" + e

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
        assert(enum is None or isinstance(enum, FieldEnum))
        
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
    def field_bytetype(self):
        return "uint{}_t".format(8 if self.bitsize <= 8 else 16)

    @property
    def field_type(self):
        if self.enum is None:
            return "uint{}_t".format(8 if self.bitsize <= 8 else 16)
        else:
            return self.enum.name

    def __repr__(self):
        return "Field{{ {} ({}): off={}, size={} {}}}".format(self.name, self.field_type, self.offset, self.bitsize, "enum={}".format(self.enum) if self.enum is not None else "")

class Node(object):
    def __init__(self, common_enums, all_fields, parent, name, subcat=None, children=None, fields=None, senders=None):
        self.name = name

        self.parent = parent
        
        # self.fields = [Field(**fa) for fa in fields] if fields is not None else []
        self.fields = None
        if fields is not None:
            self.fields = []
            for fa in fields:
                if 'enum_name' in fa:
                    fa2 = {k:fa[k] for k in fa if k != 'enum_name'}
                    fa2['enum'] = common_enums[fa['enum_name']]
                    fa = fa2

                fa['name'] = name + fa['name']

                f = Field(**fa)
                self.fields.append(f)
                all_fields.append(f)


        self.subcat = None
        if subcat is not None :
            self.subcat = Field(name, name[0:1], enumerators=subcat)
            all_fields.append(self.subcat)

        # link to the children
        self.children = None
        self.children_field = None
        if children is not None:
            self.children = [Node(common_enums, all_fields, self, **na) for na in children]
            self.children_field = Field(name, name[0:1], enumerators=[c.name for c in self.children])
            all_fields.append(self.children_field)


        self.senders = senders if senders is not None else []

    def __repr__(self):
        return self._repr()

    def _repr(self, level=0):
        txt = "node:: " + self.name + ": "
        if self.subcat is not None:
            txt += "SubCat[" + str(self.subcat) + "] "

        if len(self.senders) > 0:
            txt += " Sender[" + ", ".join(self.senders) + "]  "

        if self.fields is not None:
            txt += "\n"
            txt += "\n".join((1+level)*"\t"+str(f) for f in self.fields)

        

        for c in self.children:
            txt += "\n\t" + level*"\t" + str(c._repr(level+1))

        return txt



