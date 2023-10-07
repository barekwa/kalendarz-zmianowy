from enum import Enum


class EntryType(Enum):
    WORK = 'work'
    BUSINESS_TRIP = 'business_trip'
    VACATION = 'vacation'
    SICK_LEAVE = 'sick_leave'


class CalendarResponse:
    def __init__(self, _id, date, entry_type, work_hours=None):
        self._id = _id
        self.date = date
        self.entry_type = entry_type
        self.work_hours = work_hours

    def to_dict(self):
        return {
            "_id": self._id,
            "date": self.date,
            "entry_type": self.entry_type.value,
            "work_hours": self.work_hours
        }


class CalendarRequest:
    def __init__(self, date, entry_type, user_id, work_hours=None):
        self.date = date
        self.entry_type = entry_type
        self.work_hours = work_hours
        self.user_id = user_id

    def to_dict(self):
        return {
            "date": self.date,
            "entry_type": self.entry_type.value,
            "work_hours": self.work_hours,
            "user_id": self.user_id
        }
