from calendar import timegm as to_timestamp
import datetime
from app import db


class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    plan_id = db.Column(db.String(32))  # Corresponds to plan ID in Stripe.
    auto_renew = db.Column(db.Boolean)  # Look into Stripe docs to do this.  Think we need to send `at_period_end=False`
                                        # when creating a subscription for non-recurring subs.
    PLAN_IDS_TO_NAMES = {
        "backtrack": "Backtrack",
        "chrono": "Chrono",
        "universe": "Universe"
    }

    def __init__(self, user_id=None, created_at=None, expires_at=None):
        self.user_id = user_id
        self.created_at = created_at
        self.expires_at = expires_at

    def __repr__(self):
        return "<Subscription {}>".format(id)

    @property
    def created_at_timestamp(self):
        return to_timestamp(self.created_at.utctimetuple())

    @property
    def plan_name(self):
        return self.PLAN_IDS_TO_NAMES.get(self.plan_id)

    @staticmethod
    def get_valid_subscriptions():
        return Subscription.query.filter(Subscription.expires_at >= datetime.datetime.utcnow()).all()


class SubscriptionLastMatch(db.Model):
    """
    Used for automatic match archiving.  Logs the last replay
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    replay_found = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, user_id=None, replay_found=None):
        self.user_id = user_id
        self.replay_found = replay_found

    def __repr__(self):
        return "SubscriptionLastMatch {}/{}>".format(self.user_id, self.created_at)

    @property
    def created_at_timestamp(self):
        return to_timestamp(self.created_at.utctimetuple())