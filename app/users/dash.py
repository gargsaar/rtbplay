from app import db
from sqlalchemy import text
from flask_login import current_user


def user_performance():
    user_score_sql = text('SELECT SUM(score) FROM Score WHERE username IN (:u)')
    total_score = db.engine.execute(user_score_sql, u=current_user.username).fetchall()

    ent_cat_score_sql = text("SELECT SUM(score) FROM Score WHERE (username=:u) AND "
                             "((topic ~* '^E') OR (topic='Celebrities') OR (topic='Art'))")
    ent_score = db.engine.execute(ent_cat_score_sql, u=current_user.username).fetchall()

    multiple_cat_score_sql = text("SELECT SUM(score) FROM Score WHERE (username=:u) AND "
                                  "((topic=:c1) OR (topic=:c2) OR (topic=:c3))")
    cs_score = db.engine.execute(multiple_cat_score_sql, u=current_user.username,
                                 c1='Science: Computers', c2='Science: Gadgets', c3='Science: Mathematics').fetchall()
    gk_score = db.engine.execute(multiple_cat_score_sql, u=current_user.username,
                                 c1='General Knowledge', c2='Sports', c3='Science & Nature').fetchall()
    ss_score = db.engine.execute(multiple_cat_score_sql, u=current_user.username,
                                 c1='History', c2='Geography', c3='Politics', ).fetchall()
    other_score = db.engine.execute(multiple_cat_score_sql, u=current_user.username,
                                    c1='Vehicles', c2='Animals', c3='Mythology', ).fetchall()

    arr = [total_score[0][0], cs_score[0][0], gk_score[0][0], ss_score[0][0], ent_score[0][0], other_score[0][0]]
    arr = [0 if x is None else x for x in arr]

    return arr


def leaderboard():
    # get total_score, success_rate, points from score table
    top_score_sql = text("SELECT username, SUM(score) AS total_score, ROUND(AVG(score)*1,0) AS success_rate, "
                         "FLOOR(SUM(score)*AVG(score)) AS points FROM Score GROUP BY username ORDER BY points DESC")
    top_score = db.engine.execute(top_score_sql).fetchall()

    # get country from account table
    country_sql = text("SELECT DISTINCT username, predicted_country FROM account")
    country = db.engine.execute(country_sql).fetchall()

    # join score and country to create an array lb_updated
    lb_updated = []
    temp = []

    for row in top_score:
        for column in row:
            temp.append(column)
        lb_updated.append(temp)
        temp = []

    for x in top_score:
        for y in country:
            if x[0] == y[0]:
                for z in lb_updated:
                    if z[0] == y[0]:
                        z.append(y[1])
                        break

    return lb_updated