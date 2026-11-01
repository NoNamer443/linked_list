from typing import Self
from dataclasses import dataclass
from abc import ABCMeta, abstractmethod
from collections.abc import Iterable

@dataclass(repr=False, slots=True, eq=False, match_args=False, weakref_slot=True)
class Node[T]:
    data: T
    next: None | Self = None


class LinkedIterator[T](metaclass=ABCMeta):
    __slots__ = ("node",)

    def __init__(self, /, start: None | Node[T]) -> None:
        self.node = start

    def __iter__(self, /) -> Self:
        return self

    @abstractmethod
    def __next__(self, /):
        raise NotImplementedError


class DataIterator[T](LinkedIterator[T]):
    __slots__ = ()

    def __next__(self, /) -> T:
        if self.node is None:
            raise StopIteration
        result = self.node.data
        self.node = self.node.next
        return result


class NodeIterator[T](LinkedIterator[T]):
    __slots__ = ()

    def __next__(self) -> Node[T]:
        if self.node is None:
            raise StopIteration
        result = self.node
        self.node = self.node.next
        return result


class LinkedList[T]:
    __slots__ = ("node",)

    @classmethod
    def _from_node(cls, node: Node[T]) -> Self:
        result = cls.__new__(cls)
        result.node = node
        return result

    @classmethod
    def create(cls, data: Iterable[T]) -> Self:
        it = iter(data)
        try:
            first = next(it)
        except StopIteration:
            raise ValueError("data was empty") from None

        result = cls(first)
        tail = result.node
        for i in it:
            tail.next = Node(i)
            tail = tail.next
        return result

    def __init__(self, /, data: T) -> None:
        self.node = Node(data)

    def __iter__(self, /) -> DataIterator[T]:
        return DataIterator(self.node)

    def iter_node(self, /) -> NodeIterator[T]:
        return NodeIterator(self.node)

    def add_at_head(self, /, data: T) -> None:
        self.node = Node(data, self.node)

    def add_at_tail(self, /, data: T) -> None:
        node = self.node
        while node.next is not None:
            node = node.next
        node.next = Node(data)