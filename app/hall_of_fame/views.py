from flask import Blueprint, render_template, flash, redirect, request, url_for, current_app

from app import db
from models import HallOfFame
from flask.ext.login import current_user, login_required
from app.admin.views import AdminModelView
from app.filters import get_hero_by_id, get_hero_by_name

mod = Blueprint("hall_of_fame", __name__, url_prefix="/hall_of_fame")

mod.add_app_template_filter(get_hero_by_id)
mod.add_app_template_filter(get_hero_by_name)


@mod.route("/")
@mod.route("/<int:week>/")
def hall_of_fame(week=None):

    entry = None
    if week is None:
        entry = HallOfFame.query.order_by(HallOfFame.week.desc()).first()

    pagination = HallOfFame.query.paginate(entry.adjusted_week if entry else week, 1, False)
    entry = entry or pagination.items[0]

    return render_template("hall_of_fame/hall_of_fame.html", entry=entry, pagination=pagination)


class HallOfFameAdmin(AdminModelView):
    column_display_pk = True

    def __init__(self, session, **kwargs):
        # Just call parent class with predefined model.
        super(HallOfFameAdmin, self).__init__(HallOfFame, session, **kwargs)