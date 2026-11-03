from typing import Self
from dataclasses import dataclass
from abc import ABCMeta, abstractmethod
from collections.abc import Iterable

@dataclass(repr=False, slots=True, eq=False, weakref_slot=True)
class Node[T]:
    """单向链表节点"""
    data: T
    next: None | Self = None

@dataclass(slots=True, weakref_slot=True)
class CycleInfo:
    """链表环信息"""
    start: int
    length: int


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

    def cycle_info(self, /) -> None | CycleInfo:
        """获取链表环信息，无环返回 `None`"""
        slow = fast = self.head
        while fast is not None and fast.next is not None:
            assert slow is not None
            slow = slow.next
            fast = fast.next.next
            if slow is fast:
                # 1. 找环入口（同时数入口索引）
                entry = self.head
                assert slow is not None
                start = 0
                while entry is not slow:
                    assert entry is not None
                    assert slow is not None
                    entry = entry.next
                    slow = slow.next
                    start += 1
                assert entry is not None

                # 2. 数环长（从入口绕一圈）
                length = 1
                node = entry.next
                assert node is not None
                while node is not entry:
                    node = node.next
                    assert node is not None
                    length += 1

                return CycleInfo(start, length)
        return None