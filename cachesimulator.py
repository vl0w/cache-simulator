import numpy as np

ADDRESS_LENGTH_BITS = 64


def _number_to_bit_str(nbr, final_length):
    bit_string = "{0:b}".format(nbr)
    zeros_needed = final_length - len(bit_string)
    assert (zeros_needed >= 0)
    return "0" * zeros_needed + bit_string


def _bit_str_to_number(bit_string):
    return int(bit_string, 2)


class Variable:
    def __init__(self, address: str):
        self.address = address

    def get_address(self) -> str:
        return self.address

    def simulate_read(self, cache):
        if cache.is_in_cache(self):
            cache.stats["hits"] += 1
        else:
            cache.stats["misses"] += 1
        cache.put_to_cache(self)
        cache.stats["accesses"] += 1

    def simulate_write(self, cache):
        self.simulate_read(cache)


class CacheLine:
    def __init__(self):
        self.tag = None
        self.timestamp = -1

    def is_empty(self):
        return self.tag is None

    def is_filled(self):
        return not self.is_empty()

    def is_older_than(self, other):
        assert (self.timestamp != -1)
        assert (other.timestamp != -1)
        return self.timestamp < other.timestamp

    def put(self, timestamp, tag):
        self.tag = tag
        self.timestamp = timestamp


class Cache:

    def __init__(self, total_size, block_size, associativity=1):
        b_float = np.log2(block_size)
        e_float = np.log2(associativity)
        if not b_float.is_integer():
            raise AttributeError("block size needs to be exponential with base 2")
        if not e_float.is_integer():
            raise AttributeError("associativity needs to be exponential with base 2")
        if not np.log2(total_size).is_integer():
            raise AttributeError("total cache size needs to be exponential with base 2")

        self.b = int(b_float)
        self.e = int(e_float)
        self.B = int(block_size)
        self.E = int(associativity)
        self.S = int(total_size / block_size / associativity)
        self.s = int(np.log2(self.S))
        self.counter = 0  # for age of cache lines
        self.stats = {
            "hits": 0,
            "misses": 0,
            "accesses": 0
        }

        self.lines = []
        for _ in range(self.S):
            set_lines = []
            for _ in range(self.E):
                set_lines.append(CacheLine())
            self.lines.append(set_lines)

    def get_offset_bits(self, var: Variable) -> str:
        return var.get_address()[-self.b:]

    def get_set_bits(self, var: Variable) -> str:
        return var.get_address()[-self.b - self.s: -self.b]

    def get_set_index(self, var: Variable) -> int:
        set_bits = self.get_set_bits(var)
        if set_bits == "":
            return 0
        else:
            return _bit_str_to_number(set_bits)

    def get_tag_bits(self, var: Variable):
        return var.get_address()[0:-self.b - self.s]

    def is_in_cache(self, var: Variable) -> bool:
        return self.__get_line(var) is not None

    def __is_set_full(self, set):
        for line in self.lines[set]:
            if line.is_empty():
                return False
        return True

    def __get_line(self, var):
        tag_bits = self.get_tag_bits(var)
        set = self.get_set_index(var)

        for line in self.lines[set]:
            if line.is_filled() and line.tag == tag_bits:
                return line

        return None

    def __get_lru_line(self, set):
        lru_line = None
        curr_min = self.counter
        for l in self.lines[set]:
            if l.timestamp < curr_min:
                curr_min = l.timestamp
                lru_line = l

        assert (lru_line is not None)
        return lru_line

    def put_to_cache(self, var: Variable):
        self.counter += 1
        if self.is_in_cache(var):
            line = self.__get_line(var)
            line.timestamp = self.counter
            return

        tag_bits = self.get_tag_bits(var)
        set = self.get_set_index(var)

        cached = False
        for line in self.lines[set]:
            if line.is_empty():
                line.put(self.counter, tag_bits)
                cached = True
                break

        if cached:
            return

        lru_line = self.__get_lru_line(set)
        lru_line.put(self.counter, tag_bits)

    def print_var_info(self, var: Variable):
        offset_bits = self.get_offset_bits(var)
        set_bits = self.get_set_bits(var)
        tag_bits = self.get_tag_bits(var)

        print("Variable: " + var.get_address())
        print("Offset bits: {}, Offset: {}".format(offset_bits, _bit_str_to_number(offset_bits)))
        print("Tag bits: {}, Tag: {}".format(tag_bits, _bit_str_to_number(tag_bits)))
        print("Set bits: {}, Set: {}".format(set_bits, _bit_str_to_number(set_bits)))

    def get_total_size(self):
        return self.S * self.E * self.B


def create_variables(start_address_int: int, amount: int, size_per_var: int):
    vars = []
    curr_address_int = start_address_int
    for _ in range(amount):
        curr_address_string = _number_to_bit_str(curr_address_int, ADDRESS_LENGTH_BITS)
        vars.append(Variable(curr_address_string))
        curr_address_int += size_per_var
    return vars


def create_floats(start_address_int: int, amount: int):
    return create_variables(start_address_int, amount, 4)


def create_doubles(start_address_int: int, amount: int):
    return create_variables(start_address_int, amount, 8)
