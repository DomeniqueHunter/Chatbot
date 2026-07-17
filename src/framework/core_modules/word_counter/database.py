from __future__ import annotations

from datetime import date, datetime


class WordCounterDB:

    def __init__(self) -> None:
        self.data = {}
        self.window_size = 5

    def add(self, channel:str, user:str, number:int) -> None:
        today = WordCounterDB.today_key()
        self.ensure_day(today)
        channel_data = self.data[today].setdefault(channel, {})
        channel_data[user] = channel_data.get(user, 0) + number

    def get_day(self, date_key:str, channel:str, user:str) -> int:
        return self.data.get(date_key, {}).get(channel, {}).get(user, 0)

    def get_total(self, channel:str, user:str) -> int:
        return sum(day_data.get(channel, {}).get(user, 0) for day_data in self.data.values())

    def statistics(self) -> list:
        totals = {}
        for day_data in self.data.values():
            for channel_data in day_data.values():
                for user, count in channel_data.items():
                    totals[user] = totals.get(user, 0) + count
                    
        return sorted(totals.items(), key=lambda item: item[1], reverse=True)

    def ensure_day(self, date_key:str=None) -> bool:
        if date_key == None:
            date_key = self.today_key()
            
        if date_key not in self.data:
            self.data[date_key] = {}
            self._cleanup()
            return True
        
        return False

    def _cleanup(self) -> None:
        while len(self.data) > self.window_size:
            oldest_key = min(self.data, key=self._parse_date)
            del self.data[oldest_key]

    @staticmethod
    def _parse_date(date_key:str) -> datetime:
        return datetime.strptime(date_key, '%Y-%m-%d')

    @staticmethod
    def today_key() -> str:
        return date.today().strftime('%Y-%m-%d')
