from sqlalchemy import Column, String, Integer, Boolean, ForeignKey

from persistent.model import Model


class CityUserData(Model):
    REQUEST_CLASS = "StartupService"
    __tablename__ = 'CityUserData'

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('Account.user_name'))

    player_id = Column(String)
    city_name = Column(String)
    user_name = Column(String)
    era = Column(String)
    is_tester = Column(Boolean)
    profile_text = Column(String)
    portrait_id = Column(String)
    # unlocked_avatars = Column(String)
    clan_name = Column(String)
    email_validated = Column(Boolean)
    time_left_to_validate_email = Column(Boolean)
    has_new_event = Column(Boolean)
    has_new_neighbors = Column(Boolean)
    is_guest = Column(Boolean)
    hasPiiAccess = Column(Boolean)
    canSetEmail = Column(Boolean)
    isRealEmail = Column(Boolean)
    createdAt = Column(Integer)
    rank = Column(String, default='')

    def __init__(self, *args, **kwargs):
        super(CityUserData, self).__init__(*args, **kwargs)

    def __repr__(self):
        return "Account %s" % self.user_name

    def populate(self, *args, **kwargs):
        return super(CityUserData, self).populate(*args, **kwargs)
