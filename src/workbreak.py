from datetime import datetime


class WorkBreak:
    def __init__(self, start, end):
        '''Initialization method.

        Parameters:
            start (datetime): The start time of the break.
            end (datetime): The start time of the break.
        '''
        if not isinstance(start, datetime) or not isinstance(end, datetime):
            raise TypeError

        if start > end:
            raise RuntimeWarning('Start date is greater than end date!')

        self.start = start
        self.end = end

    def intersects(self, brk):
        '''Returns whether the two breaks intersect or not.

        Parameters:
            brk (WorkBreak): The other work break.

        Returns:
            bool: True if the breaks intersect, false otherwise.
        '''
        if not isinstance(brk, WorkBreak):
            raise TypeError

        # Checks if an intersections occur
        if self.start <= brk.start and self.end >= brk.end:  # The other is a subset of this
            return True
        elif self.start > brk.start and self.end < brk.end:  # This is a subset of the other
            return True
        elif self.start <= brk.start <= self.end:  # The other starts within this
            return True
        elif self.start <= brk.end <= self.end:  # The other ends within this
            return True

        return False

    def join(self, brk):
        '''Returns a join of the two work breaks if they intersect.

        Parameters:
            brk (WorkBreak): The other work break.

        Returns:
            WorkBreak: The join of the two breaks if they intersect, None otherwise.
        '''
        if not isinstance(brk, WorkBreak):
            raise TypeError

        result = None

        # Checks if the breaks intersect
        if self.intersects(brk):
            start = min(self.start, brk.start)
            end = max(self.end, brk.end)
            result = WorkBreak(start, end)

        return result

    def seconds(self, start, end):
        '''Finds the number of seconds from the break within the session.

        Parameters:
            start (datetime): The start time of the session.
            end (datetime): The end time of the session.

        Returns:
            int: The number of seconds from the break that are within the session.
        '''
        if not isinstance(start, datetime) or not isinstance(end, datetime):
            raise TypeError

        if start > end:
            raise RuntimeWarning('Start date is greater than end date!')

        # Assume the session does not intersect with the break
        seconds = 0

        # Cases where the session does intersect with the break
        if self.start >= start and self.end <= end:  # The break is a subset of the session
            seconds = (self.end - self.start).total_seconds()
        elif self.start < start and self.end > end:  # The session is a subset of the break
            seconds = (end - start).total_seconds()
        elif self.end > end >= self.start >= start:  # The break's end is after the session's
            seconds = (end - self.start).total_seconds()
        elif self.start < start <= self.end <= end:  # The break's start is before the session's
            seconds = (self.end - start).total_seconds()

        return seconds
