import numpy as np
from typing import List, Dict
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass


def _number_to_bit_str(nbr, final_length):
    bit_string = "{0:b}".format(nbr)
    zeros_needed = final_length - len(bit_string)
    return "0" * zeros_needed + bit_string


def _bit_str_to_number(bit_string):
    return int(bit_string, 2)


class Variable:
    _address: str

    def __init__(self, address: str, memory_system):
        self._address = address
        self._memory_system = memory_system

    @property
    def address(self) -> str:
        return self._address

    def read(self):
        self._memory_system.read_var(self)

    def write(self):
        self._memory_system.write_var(self)


@dataclass
class CacheStats:
    hits = 0
    misses = 0
    accesses = 0


class AbstractCache(metaclass=ABCMeta):
    _stats: CacheStats
    _description: str

    def __init__(self, description=""):
        self._description = description
        self._stats = CacheStats()

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    @property
    def stats(self) -> CacheStats:
        return self._stats

    @abstractmethod
    def read_var(self, var: Variable):
        raise NotImplementedError()

    @abstractmethod
    def write_var(self, var: Variable):
        raise NotImplementedError()

    @abstractmethod
    def is_in_cache(self, var: Variable) -> bool:
        raise NotImplementedError()


class MemorySystem:
    _address_length: int
    _next_variable_byte_pos_int: int
    _caches: List[AbstractCache]

    def __init__(self, address_length: int = 64):
        self._address_length = address_length
        self._next_variable_byte_pos_int = 0
        self._caches = []

    @property
    def address_length(self) -> int:
        return self._address_length

    @property
    def caches(self) -> List[AbstractCache]:
        return self._caches

    def add_cache(self, cache: AbstractCache):
        self._caches.append(cache)

    def create_variables(self, amount: int, bytes_per_var: int) -> List[Variable]:
        variables: List[Variable] = []
        for _ in range(amount):
            curr_address_string = _number_to_bit_str(self._next_variable_byte_pos_int, self._address_length)
            variables.append(Variable(curr_address_string, self))
            self._next_variable_byte_pos_int += bytes_per_var
        return variables

    def create_doubles(self, amount: int) -> List[Variable]:
        return self.create_variables(amount, 8)

    def create_floats(self, amount: int) -> List[Variable]:
        return self.create_variables(amount, 4)

    def read_var(self, var: Variable):
        for cache in self._caches:
            was_cached = cache.is_in_cache(var)
            cache.read_var(var)
            if was_cached:
                break

    def write_var(self, var: Variable):
        for cache in self._caches:
            was_cached = cache.is_in_cache(var)
            cache.write_var(var)
            if was_cached:
                break


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


class Cache(AbstractCache):
    _b: int
    _e: int
    _s: int
    _B: int
    _E: int
    _S: int
    _timestamp: int
    _sets: List[CacheSet]

    def __init__(self, total_size: int, block_size: int, associativity: int = 1, description=""):
        AbstractCache.__init__(self, description)

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

        self._sets = []
        for _ in range(self._S):
            self._sets.append(CacheSet(self._E))

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

    def read_var(self, var: Variable):
        self.__put_to_cache_and_update_stats(var)

    def write_var(self, var: Variable):
        self.read_var(var)

    def __put_to_cache_and_update_stats(self, var: Variable):
        tag_bits = self.get_tag_bits(var)
        set_index = self.get_set_index(var)
        cache_set = self._sets[set_index]

        self._timestamp += 1
        self.stats.accesses += 1

        if cache_set.is_var_cached(tag_bits):
            self.stats.hits += 1
        else:
            self.stats.misses += 1

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
