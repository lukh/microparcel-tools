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

    def text_0(self, bytecount):
        txt = ""
        for by in range(bytecount):
            txt += '|{0:02d} '.format(by)
            for bit in range(6, -1, -1):
                txt += '|   '
            txt += " |"

        return txt

    def text_1(self, bytecount):
        txt = ""
        for by in range(bytecount):
            for bit in range(7, -1, -1):
                txt += '|{0:02d} '.format(bit)
            txt += " |"

        return txt


    def text_2(self, bytecount):
        bitfield = ["|   " for i in range(bytecount * 8)]
        for i in range(self.offset, self.offset + self.bitsize, 1):
            bitfield[i] = "|" + self.short_name + " "

        txt = ""
        for by in range(bytecount):
            for bit in range(7, -1, -1):
                txt += bitfield[8*by + bit]
            txt += " |"

        return txt

class Node(object):
    def __init__(self, common_enums, all_fields, parent, name, subcat=None, children=None, fields=None, senders=None):
        assert (parent is None or isinstance(parent, Node)), "Parent of {} must be a Node or None".format(name)
        assert (subcat is None or isinstance(subcat, list)), "Subcat of {} must be None or a list of string".format(name)
        assert (children is None) ^ (fields is None), "Node {} can't have both fields and children".format(name)

        self.name = name

        self.parent = parent
        
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
        if subcat is not None:
            if len(subcat) > 255:
                raise ValueError("Can't have more that 255 values in {} subcat".format(name))
            self.subcat = Field(name, name[0:2], enumerators=subcat)
            all_fields.append(self.subcat)

        # link to the children
        self.children = None
        self.children_field = None
        if children is not None:
            if len(children) > 255:
                raise ValueError("Can't have more that 255 children in {}".format(name))
            self.children = [Node(common_enums, all_fields, self, **na) for na in children]
            self.children_field = Field(name, name[0:2], enumerators=[c.name for c in self.children])
            all_fields.append(self.children_field)


        self.senders = senders if senders is not None else []


    def leafs(self, sender=None):
        """
            Yield leaf recursively. 
            @param sender: yield only leaf of this sender
        """
        if self.children is None and (sender is None or sender in self.senders):
            yield self

        elif self.children is not None:
            for c in self.children:
                for leaf in c.leafs(sender):
                    yield leaf


    def build(self, current_offset):
        """
            Build recursively the offset.
        """
        # first of all, call the parent's build
        if self.parent is not None:
            current_offset = self.parent.build(current_offset)

        # add the children field
        if self.children_field is not None:
            self.children_field.offset = current_offset
            current_offset += self.children_field.bitsize

        #data fields
        if self.fields is not None:
            for f in self.fields:
                f.offset = current_offset
                current_offset += f.bitsize

        # sub cat field
        if self.subcat is not None:
            self.subcat.offset = current_offset
            current_offset += self.subcat.bitsize

        return current_offset