import numpy as np
from typing import List, Dict

ADDRESS_LENGTH_BITS = 64


def _number_to_bit_str(nbr, final_length):
    bit_string = "{0:b}".format(nbr)
    zeros_needed = final_length - len(bit_string)
    assert (zeros_needed >= 0)
    return "0" * zeros_needed + bit_string


def _bit_str_to_number(bit_string):
    return int(bit_string, 2)


class Variable:
    _address: str

    def __init__(self, address: str):
        self._address = address

    @property
    def address(self) -> str:
        return self._address

    def simulate_read(self, cache):
        if cache.is_in_cache(self):
            cache.stats["hits"] += 1
        else:
            cache.stats["misses"] += 1
        cache.put_to_cache(self)
        cache.stats["accesses"] += 1

    def simulate_write(self, cache):
        self.simulate_read(cache)


class CacheSet:
    _lines: Dict[str, int]  # (tag, timestamp)
    _associativity: int

    def __init__(self, associativity: int):
        self._associativity = associativity
        self._used_lines = 0
        self._lines = dict()

    def is_var_cached(self, tag: str) -> bool:
        return tag in self._lines

    def put_var(self, tag: str, timestamp: int):
        self._lines[tag] = timestamp

        if len(self._lines.values()) > self._associativity:
            self._remove_oldest_line()

    def _remove_oldest_line(self):
        self._lines.values()

        line_with_lowest_timestamp = None
        lowest_timestamp = -1
        for tag, timestamp in self._lines.items():
            if line_with_lowest_timestamp is None or timestamp < lowest_timestamp:
                lowest_timestamp = timestamp
                line_with_lowest_timestamp = tag

        self._lines.pop(line_with_lowest_timestamp)


class Cache:
    _b: int
    _e: int
    _s: int
    _B: int
    _E: int
    _S: int
    _timestamp: int
    _sets: List[CacheSet]
    _stats: Dict[str, int]

    def __init__(self, total_size: int, block_size: int, associativity: int = 1):
        b_float = np.log2(block_size)
        e_float = np.log2(associativity)
        if not b_float.is_integer():
            raise AttributeError("block size needs to be exponential with base 2")
        if not e_float.is_integer():
            raise AttributeError("associativity needs to be exponential with base 2")
        if not np.log2(total_size).is_integer():
            raise AttributeError("total cache size needs to be exponential with base 2")

        self._b = int(b_float)
        self._e = int(e_float)
        self._B = int(block_size)
        self._E = int(associativity)
        self._S = int(total_size / block_size / associativity)
        self._s = int(np.log2(self._S))
        self._timestamp = 0  # for age of cache lines
        self._stats = {
            "hits": 0,
            "misses": 0,
            "accesses": 0
        }

        self._sets = []
        for _ in range(self._S):
            self._sets.append(CacheSet(self._E))

    @property
    def stats(self) -> Dict[str, int]:
        return self._stats

    def get_offset_bits(self, var: Variable) -> str:
        return var.address[-self._b:]

    def get_set_bits(self, var: Variable) -> str:
        return var.address[-self._b - self._s: -self._b]

    def get_set_index(self, var: Variable) -> int:
        set_bits = self.get_set_bits(var)
        if set_bits == "":
            return 0
        else:
            return _bit_str_to_number(set_bits)

    def get_tag_bits(self, var: Variable) -> str:
        return var.address[0:-self._b - self._s]

    def is_in_cache(self, var: Variable) -> bool:
        tag = self.get_tag_bits(var)
        set_index = self.get_set_index(var)
        return self._sets[set_index].is_var_cached(tag)

    def put_to_cache(self, var: Variable):
        self._timestamp += 1

        tag_bits = self.get_tag_bits(var)
        set_index = self.get_set_index(var)
        cache_set = self._sets[set_index]
        cache_set.put_var(tag_bits, self._timestamp)

    def print_var_info(self, var: Variable):
        offset_bits = self.get_offset_bits(var)
        set_bits = self.get_set_bits(var)
        tag_bits = self.get_tag_bits(var)

        print("Variable: " + var.address)
        print("Offset bits: {}, Offset: {}".format(offset_bits, _bit_str_to_number(offset_bits)))
        print("Tag bits: {}, Tag: {}".format(tag_bits, _bit_str_to_number(tag_bits)))
        print("Set bits: {}, Set: {}".format(set_bits, _bit_str_to_number(set_bits)))

    def get_total_size(self) -> int:
        return self._S * self._E * self._B


def create_variables(start_address_int: int, amount: int, size_per_var: int) -> List[Variable]:
    variables: List[Variable] = []
    curr_address_int = start_address_int
    for _ in range(amount):
        curr_address_string = _number_to_bit_str(curr_address_int, ADDRESS_LENGTH_BITS)
        variables.append(Variable(curr_address_string))
        curr_address_int += size_per_var
    return variables


def create_floats(start_address_int: int, amount: int) -> List[Variable]:
    return create_variables(start_address_int, amount, 4)


def create_doubles(start_address_int: int, amount: int) -> List[Variable]:
    return create_variables(start_address_int, amount, 8)
