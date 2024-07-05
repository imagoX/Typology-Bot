from telegram import Update
from telegram.ext import filters
from telegram.ext import ContextTypes
from misc import GROUP_ID, GROUP_ID2, TEST_GROUP_ID

class MessageFilter(filters.UpdateFilter):
    def __init__(self, startup_time):
        super().__init__()
        self.startup_time = startup_time

    def filter(self, update: Update) -> bool:
        if update.message:
            return update.message.date > self.startup_time
        return False

class CustomFilters:
    class SpecificGroupFilter(filters.BaseFilter):
        def filter(self, message):
            return message.chat.id in [GROUP_ID, GROUP_ID2, TEST_GROUP_ID]

    specific_group = SpecificGroupFilter()