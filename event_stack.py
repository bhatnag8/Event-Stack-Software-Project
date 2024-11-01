# event_stack.py

class Event:
    def __init__(self, event_type, event_time, details=None):
        self.event_type = event_type
        self.event_time = event_time
        self.details = details

class Node:
    def __init__(self, event):
        self.event = event
        self.next = None
        self.prev = None

class EventStack:
    def __init__(self):
        self.head = None
        self.tail = None

    def insert_event(self, event):
        new_node = Node(event)
        if not self.head:
            self.head = self.tail = new_node
        else:
            current = self.head
            while current and current.event.event_time <= event.event_time:
                current = current.next
            if current == self.head:
                new_node.next = self.head
                self.head.prev = new_node
                self.head = new_node
            elif not current:
                self.tail.next = new_node
                new_node.prev = self.tail
                self.tail = new_node
            else:
                prev_node = current.prev
                prev_node.next = new_node
                new_node.prev = prev_node
                new_node.next = current
                current.prev = new_node

    def pop_next_event(self):
        if not self.head:
            return None
        next_event = self.head.event
        self.head = self.head.next
        if self.head:
            self.head.prev = None
        else:
            self.tail = None
        return next_event

    def is_empty(self):
        return self.head is None
