from haystack.signals import RealtimeSignalProcessor
from haystack.utils import get_identifier

from celery_haystack.utils import get_update_task


class CelerySignalProcessor(RealtimeSignalProcessor):
    """
    A ``RealtimeSignalProcessor`` subclass that enqueues updates/deletes for later
    processing using Celery.
    """
    def __init__(self, *args, **kwargs):
        super(CelerySignalProcessor, self).__init__(*args, **kwargs)
        self.task_cls = get_update_task()

    def handle_save(self, instance, sender, **kwargs):
        if not getattr(instance, 'skip_indexing', False):
            self.enqueue_save(instance, **kwargs)

    def handle_delete(self, instance, sender, **kwargs):
        if not getattr(instance, 'skip_indexing', False):
            self.enqueue_delete(instance, **kwargs)

    def enqueue_save(self, instance, **kwargs):
        return self.enqueue('update', instance)

    def enqueue_delete(self, instance, **kwargs):
        return self.enqueue('delete', instance)

    def enqueue(self, action, instance):
        """
        Shoves a message about how to update the index into the queue.

        This is a standardized string, resembling something like::

            ``notes.note.23``
            # ...or...
            ``weblog.entry.8``
        """
        return self.task_cls.delay(action, get_identifier(instance))
