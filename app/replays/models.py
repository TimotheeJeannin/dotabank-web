from app import db
from flask.ext.login import current_user
import datetime


# noinspection PyShadowingBuiltins
class Replay(db.Model):
    __tablename__ = "replays"

    id = db.Column(db.Integer, primary_key=True)  # optional uint32 match_id = 6;
    url = db.Column(db.String(80))  # TODO: Make property method, instead of being a column.
    local_uri = db.Column(db.String(128))
    state = db.Column(db.Enum(
        "WAITING_GC",
        "WAITING_DOWNLOAD",
        "DOWNLOAD_IN_PROGRESS",
        "ARCHIVED",
        "GC_ERROR",
        "DOWNLOAD_ERROR"
    ), default="WAITING_GC")
    gc_fails = db.Column(db.Integer, default=0)
    dl_fails = db.Column(db.Integer, default=0)

    # Timestamps for progress tracker
    added_to_site_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    gc_done_time = db.Column(db.DateTime)
    dl_done_time = db.Column(db.DateTime)

    # Match data
    replay_state = db.Column(db.Enum(
        "REPLAY_AVAILABLE",
        "REPLAY_NOT_RECORDED",
        "REPLAY_EXPIRED",
        "UNKNOWN"
    ), default="UNKNOWN")  # optional .CMsgDOTAMatch.ReplayState replay_state = 34 [default = REPLAY_AVAILABLE];
    replay_cluster = db.Column(db.Integer())  # optional uint32 cluster = 10;
    replay_salt = db.Column(db.Integer())  # optional fixed32 replay_salt = 13;

    game_mode = db.Column(db.SmallInteger())  # optional .DOTA_GameMode game_mode = 31 [default = DOTA_GAMEMODE_NONE];
    match_seq_num = db.Column(db.Integer())  # optional uint64 match_seq_num = 33;
    lobby_type = db.Column(db.SmallInteger())  # optional uint32 lobby_type = 16;
    league_id = db.Column(db.Integer())  # optional uint32 leagueid = 22;
    series_id = db.Column(db.Integer())  # optional uint32 series_id = 39;
    series_type = db.Column(db.Integer())  # optional uint32 series_type = 40;

    good_guys_win = db.Column(db.Boolean())  # optional bool good_guys_win = 2;
    duration = db.Column(db.Integer())  # optional uint32 duration = 3;
    start_time = db.Column(db.Integer())  # optional fixed32 startTime = 4;
    first_blood_time = db.Column(db.Integer())  # optional uint32 first_blood_time = 12;
    human_players = db.Column(db.Integer())  # optional uint32 human_players = 17;

    radiant_tower_status = db.Column(db.Integer())  # repeated uint32 tower_status = 8;
    dire_tower_status = db.Column(db.Integer())
    radiant_barracks_status = db.Column(db.Integer())  # repeated uint32 barracks_status = 9;
    dire_barracks_status = db.Column(db.Integer())

    radiant_team_id = db.Column(db.Integer())  # optional uint32 radiant_team_id = 20;
    radiant_team_name = db.Column(db.String(80))  # optional string radiant_team_name = 23;
    radiant_team_logo = db.Column(db.BigInteger())  # optional uint64 radiant_team_logo = 25;
    radiant_team_tag = db.Column(db.String(80))  # optional string radiant_team_tag = 37;
    radiant_team_complete = db.Column(db.Boolean())  # optional uint32 radiant_team_complete = 27;

    dire_team_id = db.Column(db.Integer())  # optional uint32 dire_team_id = 21;
    dire_team_name = db.Column(db.String(80))  # optional string dire_team_name = 24;
    dire_team_logo = db.Column(db.BigInteger())  # optional uint64 dire_team_logo = 26;
    dire_team_tag = db.Column(db.String(80))  # optional string dire_team_tag = 38;
    dire_team_complete = db.Column(db.Boolean())  # optional uint32 dire_team_complete = 28;

    radiant_guild_id = db.Column(db.Integer())  # optional uint32 radiant_guild_id = 35;
    dire_guild_id = db.Column(db.Integer())  # optional uint32 dire_guild_id = 36;

    # Not implementing
    # optional fixed32 server_ip = 14;  # Not exposed to client
    # optional uint32 server_port = 15;  # Not exposed to client
    # optional uint32 average_skill = 18;  # Not exposed to client
    # optional float game_balance = 19;  # Not exposed to client
    # optional uint32 positive_votes = 29;  # Variable, not worth serializing to DB.  Perhaps memcached with websockets GC reqs
    # optional uint32 negative_votes = 30;  # Variable, not worth serializing to DB.

    # GC relationships
    players = db.relationship('ReplayPlayer', backref="replay", lazy="dynamic", cascade="all, delete-orphan")  # repeated .CMsgDOTAMatch.Player players = 5;
    # repeated .CMatchHeroSelectEvent picks_bans = 32;  # TODO

    # Site relationships
    ratings = db.relationship('ReplayRating', backref='replay', lazy='joined', cascade="all, delete-orphan")
    favourites = db.relationship('ReplayFavourite', backref='replay', lazy='joined', cascade="all, delete-orphan")
    downloads = db.relationship('ReplayDownload', backref="replay", lazy="dynamic", cascade="all, delete-orphan")

    # Set default order by
    __mapper_args__ = {
        "order_by": [db.desc(added_to_site_time)]
    }

    def __init__(self, _id=None, url="", replay_state="UNKNOWN", state="WAITING_GC"):
        self.id = _id
        self.url = url
        self.replay_state = replay_state
        self.state = state

    def __repr__(self):
        return "<Replay {}>".format(self.id)

    def user_rating(self):
        if current_user.is_authenticated():
            return next((rating for rating in self.ratings if rating.user_id == current_user.id), None)
        else:
            return None

    def user_favourite(self):
        if current_user.is_authenticated():
            return next((favourite for favourite in self.favourites if favourite.user_id == current_user.id), False)
        else:
            return False


# noinspection PyShadowingBuiltins
class ReplayRating(db.Model):
    __tablename__ = "replay_ratings"

    id = db.Column(db.Integer, primary_key=True)
    replay_id = db.Column(db.Integer, db.ForeignKey("replays.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    positive = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, replay_id=None, user_id=None, positive=None):
        self.replay_id = replay_id
        self.user_id = user_id
        self.positive = positive

    def __repr__(self):
        return "<Rating {}/{}>".format(self.replay_id, self.user_id)


# noinspection PyShadowingBuiltins
class ReplayFavourite(db.Model):
    __tablename__ = "replay_favs"

    id = db.Column(db.Integer, primary_key=True)
    replay_id = db.Column(db.Integer, db.ForeignKey("replays.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    def __init__(self, replay_id=None, user_id=None):
        self.replay_id = replay_id
        self.user_id = user_id

    def __repr__(self):
        return "<Favourite {}/{}>".format(self.replay_id, self.user_id)


# noinspection PyShadowingBuiltins
class ReplayDownload(db.Model):
    __tablename__ = "replay_downloads"

    id = db.Column(db.Integer, primary_key=True)
    replay_id = db.Column(db.Integer, db.ForeignKey("replays.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    def __init__(self, replay_id=None, user_id=None):
        self.replay_id = replay_id
        self.user_id = user_id

    def __repr__(self):
        return "<Download {}/{}>".format(self.replay_id, self.user_id)


class ReplayPlayer(db.Model):
    __tablename__ = "replay_players"

    id = db.Column(db.Integer, primary_key=True)
    replay_id = db.Column(db.Integer, db.ForeignKey("replays.id", ondelete="CASCADE"), nullable=False)

    # GC data
    account_id = db.Column(db.Integer)  # optional uint32 account_id = 1;
    player_slot = db.Column(db.Integer)  # optional uint32 player_slot = 2;
    hero_id = db.Column(db.Integer)  # optional uint32 hero_id = 3;
    item_0 = db.Column(db.Integer)  # optional uint32 item_0 = 4;
    item_1 = db.Column(db.Integer)  # optional uint32 item_1 = 5;
    item_2 = db.Column(db.Integer)  # optional uint32 item_2 = 6;
    item_3 = db.Column(db.Integer)  # optional uint32 item_3 = 7;
    item_4 = db.Column(db.Integer)  # optional uint32 item_4 = 8;
    item_5 = db.Column(db.Integer)  # optional uint32 item_5 = 9;
    kills = db.Column(db.Integer)  # optional uint32 kills = 14;
    deaths = db.Column(db.Integer)  # optional uint32 deaths = 15;
    assists = db.Column(db.Integer)  # optional uint32 assists = 16;
    leaver_status = db.Column(db.SmallInteger)  # optional uint32 leaver_status = 17;
    gold = db.Column(db.Integer)  # optional uint32 gold = 18;
    last_hits = db.Column(db.Integer)  # optional uint32 last_hits = 19;
    denies = db.Column(db.Integer)  # optional uint32 denies = 20;
    gold_per_min = db.Column(db.Integer)  # optional uint32 gold_per_min = 21;
    xp_per_min = db.Column(db.Integer)  # optional uint32 XP_per_min = 22;
    gold_spent = db.Column(db.Integer)  # optional uint32 gold_spent = 23;
    hero_damage = db.Column(db.Integer)  # optional uint32 hero_damage = 24;
    tower_damage = db.Column(db.Integer)  # optional uint32 tower_damage = 25;
    hero_healing = db.Column(db.Integer)  # optional uint32 hero_healing = 26;
    level = db.Column(db.SmallInteger)  # optional uint32 level = 27;

    # Not exposed to client (as far as I can tell)
    # optional float expected_team_contribution = 10;
    # optional float scaled_metric = 11;
    # optional uint32 previous_rank = 12;
    # optional uint32 rank_change = 13;
    # optional uint32 time_last_seen = 28;
    # optional string player_name = 29;
    # optional uint32 support_ability_value = 30;
    # optional bool feeding_detected = 32;
    # optional uint32 search_rank = 34;
    # optional uint32 search_rank_uncertainty = 35;
    # optional int32 rank_uncertainty_change = 36;
    # optional uint32 hero_play_count = 37;
    # optional fixed64 party_id = 38;
    # optional float scaled_kills = 39;
    # optional float scaled_deaths = 40;
    # optional float scaled_assists = 41;
    # optional uint32 claimed_farm_gold = 42;
    # optional uint32 support_gold = 43;
    # optional uint32 claimed_denies = 44;
    # optional uint32 claimed_misses = 45;
    # optional uint32 misses = 46;

    # TODO: Add models for these objects
    # repeated .CMatchPlayerAbilityUpgrade ability_upgrades = 47;
    # repeated .CMatchAdditionalUnitInventory additional_units_inventory = 48;

    def __init__(self, replay_id):
        self.replay_id = replay_id

    @property
    def team(self):
        if self.player_slot < 128:
            return "Radiant"
        else:
            return "Dire"

    @property
    def items(self):
        return [
            self.item_0,
            self.item_1,
            self.item_2,
            self.item_3,
            self.item_4,
            self.item_5
        ]

    def __repr__(self):
        return "<ReplayPlayer {}>".format(self.id)
