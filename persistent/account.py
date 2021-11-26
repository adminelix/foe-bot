from sqlalchemy import Column, Integer, String

from persistent.model import Model


class Account(Model):
    REQUEST_CLASS = "StartupService"
    __tablename__ = 'account'

    player_id = Column(Integer, primary_key=True, default=0)
    id = Column(String, default=0)
    user_name = Column(String, default='', unique=True)

    def __init__(self, *args, **kwargs):
        super(Account, self).__init__(*args, **kwargs)

    def __repr__(self):
        return "Account %s (%s)" % (self.player_id, self.user_name)