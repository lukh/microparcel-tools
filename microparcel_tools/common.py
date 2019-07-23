from math import ceil

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
    def __init__(self, common_enums, parent, name, subcat=None, children=None, fields=None, senders=None):
        assert (parent is None or isinstance(parent, Node)), "Parent of {} must be a Node or None".format(name)
        assert (subcat is None or isinstance(subcat, list)), "Subcat of {} must be None or a list of string".format(name)
        assert (children is None) ^ (fields is None), "Node {} can't have both fields and children".format(name)
        assert not ((senders is None) and (children is None))
        
        self.name = name

        self.parent = parent

        # link to the children
        self.children = None
        self.children_field = None
        if children is not None:
            if len(children) > 255:
                raise ValueError("Can't have more that 255 children in {}".format(name))
            self.children = [Node(common_enums, self, **na) for na in children]
            self.children_field = Field(name, name[0:2], enumerators=[c.name for c in self.children])


        self.subcat = None
        if subcat is not None:
            if len(subcat) > 255:
                raise ValueError("Can't have more that 255 values in {} subcat".format(name))
            self.subcat = Field(name, name[0:2], enumerators=subcat)

        # data fields
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


        self.senders = senders if senders is not None else []


    def parents(self, with_root=False):
        """
            yield parent recursively, starting from itself, and avoiding the root node...
        """
        if self.parent is not None:
            for p in self.parent.parents(with_root=with_root):
                yield p
            yield self

        elif with_root:
            yield self

    def need_process(self, sender):
        """
            returns True if this node or one of its children needs a process method as a sender.
        """
        if self.children is None and self.fields is not None:
            return sender not in self.senders
        if self.children is not None:
            return any([ c.need_process(sender) for c in self.children ])

    def leafs(self, sender=None, all_but_sender=False):
        """
            Yield leaf recursively. 
            @param sender: yield only leaf of this sender
            @param all_but_sender: if True, returns the leafs of all others senders than the one specified
        """
        if self.children is None and (sender is None or ((sender in self.senders) ^ all_but_sender)):
            yield self

        elif self.children is not None:
            for c in self.children:
                for leaf in c.leafs(sender, all_but_sender):
                    yield leaf

    def fields_not_none(self):
        return self.fields is not None


    def build(self, current_offset):
        """
            Build recursively the offset.
        """
        # first of all, call the parent's build
        if self.parent is not None:
            current_offset = self.parent.build(current_offset)

        # add the children field
        if self.children_field is not None:
            if self.children_field.bitsize > 8:
                raise ValueError("children_field {} of {} is too large: {}>8".format(self.children_field.name, self.name, self.children_field.bitsize))
            self.children_field.offset = current_offset
            current_offset += self.children_field.bitsize

        # sub cat field
        if self.subcat is not None:
            if self.subcat.bitsize > 8:
                raise ValueError("subcat {} of {} is too large: {}>8".format(self.subcat.name, self.name, self.subcat.bitsize))
            self.subcat.offset = current_offset
            current_offset += self.subcat.bitsize
        
        big_fields_offset = 0
        #data fields
        if self.fields is not None:
            big_fields = [f for f in self.fields if f.bitsize > 8]
            small_fields = [f for f in self.fields if f.bitsize <= 8]


            big_fields_offset = current_offset


            if len( big_fields ) == 0:
                for f in small_fields:
                    f.offset = current_offset
                    current_offset += f.bitsize

            else:
                # place the big one byte-aligned
                for f in big_fields:
                    # round up the offset
                    big_fields_offset = int ( 8 * ceil(big_fields_offset / 8.0) )
                    f.offset = big_fields_offset
                    big_fields_offset += f.bitsize

                # trying to fit the small between the last small and the first big.
                remaining_small_fields = []
                first_bf = big_fields[0]
                for sf in small_fields:
                    if sf.bitsize <= (first_bf.offset - current_offset):
                        sf.offset = current_offset
                        current_offset += sf.bitsize
                    else:
                        remaining_small_fields.append(sf)

                if len( big_fields ) > 1:
                    leftover_fields = []
                    local_curr_offs = []
                    for bf_idx in range(1, len(big_fields), 1):
                        bf0 = big_fields[bf_idx-1]

                        local_curr_offs.append(bf0.offset + bf0.bitsize)

                    for sf in remaining_small_fields:
                        for curr_off_idx, bf_idx in enumerate(range(1, len(big_fields), 1)):
                            bf1 = big_fields[bf_idx]

                            if sf.bitsize <= (bf1.offset - local_curr_offs[curr_off_idx]):
                                sf.offset = local_curr_offs[curr_off_idx]
                                local_curr_offs[curr_off_idx] += sf.bitsize
                                break

                        else:
                            leftover_fields.append(sf)


                    for f in leftover_fields:
                        f.offset = big_fields_offset
                        big_fields_offset += f.bitsize

                else: # == 1
                    for f in remaining_small_fields:
                        f.offset = big_fields_offset
                        big_fields_offset += f.bitsize




        return max(current_offset, big_fields_offset)


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

    def text_2(self, bytecount, common_fields):
        bits_list = ["|   " for i in range(bytecount*8)]

        for cf in common_fields:
            for idx in range(cf.offset, cf.offset+cf.bitsize):
                    bits_list[idx] = "|{} ".format(cf.short_name)

        for node in self.parents(with_root=True):
            if node.children_field is not None:
                for idx in range(node.children_field.offset, node.children_field.offset+node.children_field.bitsize):
                    bits_list[idx] = "|{} ".format(node.children_field.short_name)
            if node.subcat is not None:
                for idx in range(node.subcat.offset, node.subcat.offset+node.subcat.bitsize):
                    bits_list[idx] = "|{} ".format(node.subcat.short_name)
            if node.fields is not None:
                for f in node.fields:
                    for idx in range(f.offset, f.offset+f.bitsize):
                        bits_list[idx] = "|{} ".format(f.short_name)


        # invert byte
        out = []
        for b_idx in range(bytecount):
            for b in range(8):
                out.append(bits_list[(b_idx*8) + (7-b)])

        for b_idx in range(bytecount):
            out[(8*b_idx) + 7] += " |"
        return "".join(out)