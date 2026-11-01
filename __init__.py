from typing import Self
from dataclasses import dataclass
from abc import ABCMeta, abstractmethod
from collections.abc import Iterable

@dataclass(repr=False, slots=True, eq=False, match_args=False, weakref_slot=True)
class Node[T]:
    """单向链表节点"""
    data: T
    next: None | Self = None


class LinkedIterator[T](metaclass=ABCMeta):
    """单向链表迭代器基类"""
    __slots__ = ("node", "__weakref__")

    def __init__(self, /, start: None | Node[T]) -> None:
        self.node = start

    def __iter__(self, /) -> Self:
        return self

    @abstractmethod
    def __next__(self, /):
        raise NotImplementedError


class DataIterator[T](LinkedIterator[T]):
    """单向链表数据迭代器"""
    __slots__ = ()

    def __next__(self, /) -> T:
        if self.node is None:
            raise StopIteration
        result = self.node.data
        self.node = self.node.next
        return result


class NodeIterator[T](LinkedIterator[T]):
    """单向链表节点迭代器"""
    __slots__ = ()

    def __next__(self, /) -> Node[T]:
        if self.node is None:
            raise StopIteration
        result = self.node
        self.node = self.node.next
        return result


class LinkedList[T]:
    """单向链表，至少需要包含一个节点

    - `LinkedList`: 创建一个单节点链表
    - `LinkedList.from_iterable`: 从可迭代对象创建单向链表
    """
    __slots__ = ("head", "__weakref__")

    @classmethod
    def from_iterable(cls, data: Iterable[T]) -> Self:
        """从可迭代对象创建单向链表"""
        it = iter(data)
        try:
            first = next(it)
        except StopIteration:
            raise ValueError("data was empty") from None

        result = cls(first)
        tail = result.head
        for i in it:
            tail.next = Node(i)
            tail = tail.next
        return result

    def __init__(self, /, data: T) -> None:
        """创建单节点单向链表"""
        self.head = Node(data)

    def __iter__(self, /) -> DataIterator[T]:
        return DataIterator(self.head)

    def iter_node(self, /) -> NodeIterator[T]:
        return NodeIterator(self.head)

    def add_at_head(self, /, data: T) -> None:
        self.head = Node(data, self.head)

    def add_at_tail(self, /, data: T) -> None:
        node = self.head
        while node.next is not None:
            node = node.next
        node.next = Node(data)

    def __len__(self, /) -> int:
        return sum(1 for _ in self)

    def insert(self, /, index: int, data: T) -> None:
        if index < 0:
            index = len(self) + index
            if index < 0:
                index = 0
        if index == 0:
            self.add_at_head(data)
            return
        prev = self.head
        for _ in range(index - 1):
            if prev.next is None:
                break
            prev = prev.next
        prev.next = Node(data, prev.next)

    def has_cycle(self, /) -> bool:
        """判断链表是否有环"""
        slow = fast = self.head
        while fast is not None and fast.next is not None:
            assert slow is not None # Pylance真难伺候
            slow = slow.next
            fast = fast.next.next
            if slow is fast:
                return True
        return False