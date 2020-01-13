import threading
import logging
import inspect

from talon import cron, noise
from talon.voice import Context


class _LongNoiseHandler(object):
    def __init__(self, handler, gap_tolerance=0):
        # Check now to prevent deferred errors.
        self._assert_context_manager(handler)
        assert isinstance(gap_tolerance, int), type(gap_tolerance)
        self._gap_tolerance = gap_tolerance
        self._handler = handler
        self._job_lock = threading.Lock()
        self._end_job = None

    @staticmethod
    def _assert_context_manager(handler):
        if not isinstance(handler, object):
            if inspect.isclass(handler):
                raise ValueError("`handler`, must be instantiated.")
            else:
                raise ValueError("`handler` must be a context manager.")
        if not hasattr(handler, "__enter__"):
            raise ValueError(
                "`handler` must be a context manager. Had no `__enter__` method."
            )
        if not hasattr(handler, "__exit__"):
            raise ValueError(
                "`handler` must be a context manager. Had no `__enter__` method."
            )

    def on_start(self):
        try:
            with self._job_lock:
                if self._end_job:
                    cron.cancel(self._end_job)
                    self._end_job = None
            self._handler.__enter__()
        except Exception as e:
            logging.exception("Error handling noise start")

    def on_finish(self):
        if self._gap_tolerance:
            with self._job_lock:
                self._end_job = cron.after(f"{self._gap_tolerance}ms", self._exit_safe)
        else:
            self._exit_safe()

    def _exit_safe(self):
        try:
            self._handler.__exit__(None, None, None)
        except Exception as e:
            logging.exception("Error running noise end")


class _HandlerMapper(object):
    """Maps contexts to custom handlers.

    Workaround for contexts being unable to be added directly.

    """

    def __init__(self):
        self._handlers = []
        self._lock = threading.Lock()

    def add(self, context, handler, priority=0):
        """Add a new handler.

        :param Context context: the context under which this mapping is active.

        :param handler: the handler this context should map to.

        :param int priority: the priority of this mapping. Only one handler can
          be returned. If more than one context in our mapping is active, the
          one with the _largest priority_ will win. If two contexts have the
          same priority, the one added _last_ will win.

        """
        # Check now to prevent deferred errors.
        assert isinstance(context, Context)
        with self._lock:
            self._handlers.append((context, handler, priority))

    def pick(self):
        """Select the best handler to use in the current context."""
        best_handler = None
        best_priority = -1
        for (context, handler, priority) in self._handlers:
            if context.enabled and priority >= best_priority:
                best_handler = handler
                best_priority = priority
        return best_handler


class LongNoiseMapper(object):
    """Workaround to map long noises within contexts."""

    def __init__(self, noise_):
        self._handlers = _HandlerMapper()
        self.noise = noise_
        self._active_handlers = []
        self._active_handlers_lock = threading.Lock()
        noise.register(noise_, self._on_noise)

    def register(self, context, handler, priority=0, gap_tolerance=0):
        """Register a noise ``handler`` to be active in ``context``.

        Can optionally tolerate gaps in the noise.

        :param Context context: the context this handler should be active in.

        :param handler: will be called when the noise starts & stops. This
          should be an instantiated context manager - `__enter__` will be
          called when the noise starts, `__exit__` when it finishes.

        :param priority: Optional. Handlers are exclusive - only one will be
          active at a time. If multiple contexts match, the one with the
          largest ``priority`` wins (if there's a draw, the one registered last
          will win). Default is 0.

        :param float gap_tolerance: Optional. Maximum gap in the noise we will
          tolerate, in milliseconds. Gaps smaller than this value will be
          ignored. Note this will delay the `handler finishing` callback.
          Default is 0.

        """
        self._handlers.add(context, _LongNoiseHandler(handler, gap_tolerance), priority)

    def _on_noise(self, start):
        if start:
            handler = self._handlers.pick()
            if handler:
                self._handler_start(handler)
        else:
            # Stop any handlers that were activated in old contexts.
            self._finish_old_handlers()

    def _handler_start(self, handler):
        with self._active_handlers_lock:
            handler.on_start()
            # We record which handlers we've "started", so we can "finish" them
            # when the noise stops, even if the context has changed.
            self._active_handlers.append(handler)

    def _finish_old_handlers(self):
        """Call `_on_finish` for any remaining handlers."""
        with self._active_handlers_lock:
            for handler in self._active_handlers:
                handler.on_finish()
            self._active_handlers.clear()


class ShortNoiseMapper(object):
    """Workaround to map short noises within contexts."""

    def __init__(self, noise_):
        self._handlers = _HandlerMapper()
        noise.register(noise_, self._on_noise)

    def register(self, context, callback, priority=0):
        assert callable(callback), type(callback)
        self._handlers.add(context, callback, priority)

    def _on_noise(self, _):
        handler = self._handlers.pick()
        if handler:
            handler()


hiss_mapper = LongNoiseMapper("hiss")
pop_mapper = ShortNoiseMapper("pop")
