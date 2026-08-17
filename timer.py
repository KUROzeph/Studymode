from datetime import datetime


class StudyTimer:
    def __init__(self):
        self.started_at = None
        self.paused_at = None
        self.total_paused_seconds = 0

        self.running = False
        self.paused = False

    def start(self):
        if self.running:
            return

        self.started_at = datetime.now()
        self.paused_at = None
        self.total_paused_seconds = 0

        self.running = True
        self.paused = False

    def pause(self):
        if not self.running or self.paused:
            return

        self.paused_at = datetime.now()
        self.paused = True

    def resume(self):
        if not self.running or not self.paused:
            return

        pause_duration = (
            datetime.now() - self.paused_at
        ).total_seconds()

        self.total_paused_seconds += pause_duration

        self.paused_at = None
        self.paused = False

    def elapsed_seconds(self):
        if not self.running or self.started_at is None:
            return 0

        current_time = datetime.now()

        elapsed = (
            current_time - self.started_at
        ).total_seconds()

        elapsed -= self.total_paused_seconds

        if self.paused:
            elapsed -= (
                current_time - self.paused_at
            ).total_seconds()

        return max(0, int(elapsed))

    def stop(self):
        if not self.running:
            return None

        ended_at = datetime.now()
        duration = self.elapsed_seconds()

        session_data = (
            self.started_at,
            ended_at,
            duration
        )

        self.started_at = None
        self.paused_at = None
        self.total_paused_seconds = 0

        self.running = False
        self.paused = False

        return session_data