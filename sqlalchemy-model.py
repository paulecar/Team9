# coding: utf-8
from sqlalchemy import Column, DECIMAL, Date, DateTime, ForeignKey, Index, String, Table, Text, Time, text
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, TINYINT
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Kvm(Base):
    __tablename__ = 'kvm'

    key = Column(String(32), primary_key=True, unique=True)
    value = Column(String(500))


class Player(Base):
    __tablename__ = 'player'
    __table_args__ = (
        Index('surname', 'Surname', 'FirstName'),
    )

    idplayer = Column(INTEGER(11), primary_key=True, unique=True)
    Surname = Column(String(25))
    FirstName = Column(String(25))
    Active = Column(String(1), nullable=False, server_default=text("'Y'"))
    Bogged = Column(String(1))
    BoggedDate = Column(Date)


t_player_history = Table(
    'player_history', metadata,
    Column('idplayer', INTEGER(11), server_default=text("'0'")),
    Column('OpposingTeam', String(45)),
    Column('MatchDate', Date),
    Column('Playoff', String(1)),
    Column('MyPlayerRank', String(2)),
    Column('MyPLayerScore', INTEGER(11)),
    Column('OpponentName', String(45)),
    Column('OpponentRank', String(2)),
    Column('OpponentScore', INTEGER(11)),
    Column('WinLose', String(1))
)


t_player_ranking = Table(
    'player_ranking', metadata,
    Column('Player_ID', INTEGER(11)),
    Column('FirstName', String(25)),
    Column('Surname', String(25)),
    Column('MatchesPlayed', BIGINT(21), server_default=text("'0'")),
    Column('Wins', DECIMAL(23, 0)),
    Column('ActRacksWon', DECIMAL(32, 0)),
    Column('ActRacksLost', DECIMAL(32, 0)),
    Column('ActRacksPlayed', DECIMAL(33, 0)),
    Column('RacksWon', DECIMAL(32, 0)),
    Column('RacksLost', DECIMAL(32, 0)),
    Column('RacksPlayed', DECIMAL(33, 0)),
    Column('MatchPct', DECIMAL(27, 4)),
    Column('RacksPct', DECIMAL(36, 4)),
    Column('ActPct', DECIMAL(36, 4)),
    Column('idseason', INTEGER(11), server_default=text("'0'"))
)


class Season(Base):
    __tablename__ = 'season'

    idseason = Column(INTEGER(11), primary_key=True, unique=True)
    SeasonName = Column(String(45))
    SeasonStart = Column(Date)
    SeasonEnd = Column(Date)
    CurrentSeason = Column(String(1))


t_the_bog = Table(
    'the_bog', metadata,
    Column('Season_ID', INTEGER(11)),
    Column('idplayer', INTEGER(11), server_default=text("'0'")),
    Column('Surname', String(25)),
    Column('Lose', String(10)),
    Column('Win', String(10)),
    Column('Losses', DECIMAL(23, 0)),
    Column('Played', BIGINT(21), server_default=text("'0'")),
    Column('Bogged', String(1)),
    Column('BoggedDate', Date)
)


class User(Base):
    __tablename__ = 'user'

    id = Column(INTEGER(11), primary_key=True)
    UserName = Column(String(64), nullable=False)
    Email = Column(String(120), nullable=False)
    PasswordHash = Column(String(128))
    ConfCode = Column(String(8))
    Verified = Column(String(1))
    UserRole = Column(String(10))
    Player_ID = Column(INTEGER(11), comment='No FK relationship for just now, will n=be used by admin to link users')
    last_seen = Column(DateTime)
    theme = Column(String(16))


t_yrd_history = Table(
    'yrd_history', metadata,
    Column('?Match', Text),
    Column('Date', Text),
    Column('TextDate', Text),
    Column('Player', Text),
    Column('HCP', Text),
    Column('RacksWon', INTEGER(11)),
    Column('Opponent', Text),
    Column('OppHCAP', Text),
    Column('RacksLost', INTEGER(11)),
    Column('Race', INTEGER(11)),
    Column('Up/Down', INTEGER(11)),
    Column('Wire', INTEGER(11)),
    Column('WinLose', Text),
    Column('ActualRacksWon', INTEGER(11)),
    Column('ActualRacksLost', INTEGER(11)),
    Column('OpposingTeam', Text)
)


class Match(Base):
    __tablename__ = 'match'

    idmatch = Column(INTEGER(11), primary_key=True, unique=True)
    OpposingTeam = Column(String(45))
    MatchDate = Column(Date)
    Season_ID = Column(ForeignKey('season.idseason'), nullable=False, index=True)
    PlayOff = Column(String(1))
    StartTime = Column(Time)
    MatchOver = Column(String(1))

    season = relationship('Season')


class Availability(Base):
    __tablename__ = 'availability'

    idavailability = Column(INTEGER(11), primary_key=True)
    Player_ID = Column(ForeignKey('player.idplayer'), nullable=False, index=True)
    Match_ID = Column(ForeignKey('match.idmatch'), nullable=False, index=True)
    Season_ID = Column(ForeignKey('season.idseason'), nullable=False, index=True)

    match = relationship('Match')
    player = relationship('Player')
    season = relationship('Season')


class Matchup(Base):
    __tablename__ = 'matchup'

    idmatchup = Column(INTEGER(11), primary_key=True, unique=True)
    OpponentName = Column(String(45))
    MyPlayerRank = Column(String(2))
    OpponentRank = Column(String(2))
    Player_ID = Column(ForeignKey('player.idplayer'), nullable=False, index=True)
    MatchUpRace = Column(INTEGER(11))
    MyPlayerWire = Column(INTEGER(11))
    MyPlayerScore = Column(INTEGER(11))
    OpponentScore = Column(INTEGER(11))
    Match_ID = Column(ForeignKey('match.idmatch'), nullable=False, index=True)
    MyPlayerActual = Column(INTEGER(11))
    OpponentActual = Column(INTEGER(11))
    WinLose = Column(String(1))

    match = relationship('Match')
    player = relationship('Player')


class Result(Base):
    __tablename__ = 'result'

    idresult = Column(INTEGER(11), primary_key=True, unique=True)
    MatchUpsWon = Column(INTEGER(11))
    MatchUpsLost = Column(INTEGER(11))
    RacksWon = Column(INTEGER(11))
    RacksLost = Column(INTEGER(11))
    DidWeWin = Column(TINYINT(1))
    Match_ID = Column(ForeignKey('match.idmatch'), nullable=False, index=True)

    match = relationship('Match')
