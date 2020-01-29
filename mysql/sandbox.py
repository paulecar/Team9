from team9 import create_app
team9 = create_app()
team9.app_context().push()

from team9.models import Season, Match, Result, Player, Match, MatchUp
from sqlalchemy import func
from team9 import db
from pprint import pprint


def main():
    # Current matchup details to display in progress match
    results = db.session.query(Player, MatchUp, Match).join(MatchUp, Player.idplayer == MatchUp.Player_ID). \
        join(Match, Match.idmatch == MatchUp.Match_ID).filter_by(idmatch=187).order_by(MatchUp.idmatchup).all()

    parse_match_ups(results)


def parse_match_ups(results):
    match_info = dict.fromkeys(["Matches",
                                "Wins",
                                "Losses",
                                "Racks For",
                                "Racks Against",
                                "Avail For",
                                "Avail Against",
                                "Diff"], 0)

    for r in results:
        print("Match:", r.Match.idmatch, "Match Up :", r.MatchUp.idmatchup,
              "Race :", r.MatchUp.MatchUpRace, r.MatchUp.MyPlayerScore, ":", r.MatchUp.OpponentScore)
        if r.MatchUp.WinLose == "W":
            match_info["Wins"] += 1
        if r.MatchUp.WinLose == "L":
            match_info["Losses"] += 1
        if r.MatchUp.WinLose == "I":
            match_info["Avail For"] += (r.MatchUp.MatchUpRace - r.MatchUp.MyPlayerScore)
            match_info["Avail Against"] += (r.MatchUp.MatchUpRace - r.MatchUp.OpponentScore)

        match_info["Racks For"] += r.MatchUp.MyPlayerScore
        match_info["Racks Against"] += r.MatchUp.OpponentScore

    match_info["Matches"] = len(results)
    match_info["Diff"] = match_info["Racks For"] - match_info["Racks Against"]
    match_info["Max For"] = match_info["Avail For"] + match_info["Racks For"]
    match_info["Max Against"] = match_info["Avail Against"] + match_info["Racks Against"]

    pprint(match_info)

    print(can_we_win(match_info))


def can_we_win(match_info):

    # Handles situation when just one match is called
    if match_info["Matches"] == 1:
        msg = "Let's go!"
        return msg

    # Handles first round combinations where no winner can be decided yet
    if match_info["Matches"] == 2:
        if match_info["Wins"] == 0 and match_info["Losses"] == 0:
            if match_info["Racks For"] > match_info["Racks Against"]:
                msg = "Off to a good start."
            else:
                msg = "A bit shaky, but early days."
        else:
            if match_info["Wins"] > match_info["Losses"] or match_info["Racks For"] > match_info["Racks Against"]:
                msg = "Woo hoo! We're ahead."
            else:
                msg = " Nobody Panic. Not over yet."
        return msg

    # Could be decided at this point - handles 3 wins, even when last match is in progress, and the tie break stage
    if match_info["Matches"] > 2:
        if match_info["Losses"] >= 3:
            msg = "It's all over. We Suck."
            return msg
        elif match_info["Wins"] >= 3:
            msg = "It's in the bag. We Rock."
            return msg
        elif match_info["Wins"] == 2 and match_info["Losses"] == 2:
            msg = "Oh, the humanity! Tie Break decides the match."
            return msg
        # Handles intermediate situation when the last match is yet to be called
        elif match_info["Matches"] == 3:
            if match_info["Wins"] > match_info["Losses"]:
                if match_info["Racks For"] > match_info["Racks Against"]:
                    msg = "Two wins is good. We're on track."
                else:
                    msg = "Two wins is good. But we're {} racks behind, which is odd?".format(match_info["Diff"] + -1)
            else:
                if match_info["Diff"] == 0:
                    msg = "All square. Still all to play for."
                elif match_info["Diff"] > 0:
                    msg = "By no means certain of a win, but at least we are {} racks ahead.".format(match_info["Diff"])
                else:
                    msg = "We're making is hard on ourselves. Behind by {} racks.".format(match_info["Diff"] * -1)
            return msg

    # Handles all situations for the second round (3rd and 4th matches called and still no result)
    if match_info["Wins"] == 2:
        required = match_info["Max Against"] - match_info["Racks For"] + 1
        msg = "We need to win one of these matches, or win {} more racks (or {} to tie).".format(required, required - 1)
        return msg
    if match_info["Losses"] == 2:
        required = match_info["Max For"] - match_info["Racks Against"] - 1
        msg = "Gonna be rough! We need to win both of these matches, and can only lose {} more racks (or {} to tie).".\
            format(required, required + 1)
        return msg
    if match_info["Wins"] == 1 and match_info["Losses"] == 1:
        if match_info["Racks Against"] > match_info["Max For"]:
            msg = "We need to win both matches to win from here."
        elif match_info["Racks For"] > match_info["Max Against"]:
            msg = "We just need to win one of these."
        else:
            margin = match_info["Max For"] - match_info["Racks Against"]
            msg = "Gotta win one match, but can only lose {} more racks ({} for a tie).".format(margin - 1, margin)
    else:
        msg = "I'm confused. This situation is hard to figure out?"

    return msg


if __name__ == "__main__":
    main()
