import pytest

from game import Game, roll


def test__retired_player_is_available(empty_team, player):
    empty_team.players.add(player)
    empty_team.lineup.append(player)
    empty_team.retire(player)
    assert empty_team.is_available(player) is False

def test__bench_size(team):
    assert len(team.bench) == 40 - 9

def test__sub_player(team):
    entering = team.get_player_by_number(10)
    leaving  = team.get_player_by_number(1)
    team.sub_player(entering, leaving)
    assert entering in team.lineup
    assert leaving in team.retired
    assert team.is_available(entering) is True
    assert team.is_available(leaving) is False

def test__roll():
    assert 0 < roll('d4')   <   5
    assert 0 < roll('d8')   <   9
    assert 0 < roll('d10')  <  11
    assert 0 < roll('d12')  <  13
    assert 0 < roll('d20')  <  21
    assert 0 < roll('d100') < 101

    assert 0 < roll('1d4')  <   5
    assert 1 < roll('2d4')  <   9
    assert 3 < roll('4d4')  <  17
    assert 1 < roll('2d10') <  21

def test__bullpen(team):
    assert len(team.bullpen) == 10
    assert all([ p.pd for p in team.bullpen ])

def test__lineup(team):
    # lineup requires 9 numbers
    with pytest.raises(AssertionError):
        team.set_lineup(numbers=[1, 2, 3])

    # default to 1-9
    team.set_lineup()

    # set custom order
    team.set_lineup(numbers=[1, 2, 3, 7, 8, 9, 4, 5, 6])

def test__get_team_from_roster():
    game = Game()
    team = game.get_team_from_roster('tests/roster__test_team.csv')
    team.set_lineup()
    assert team.lineup[0].name == 'Winnie'

def test__game_ready__bases_empty(game_ready):
    assert game_ready.bases == [None, None, None]

def test__game_ready__bases_clear(game_ready):
    game_ready.bases.clear()
    assert game_ready.bases == [None, None, None]

def test__game_ready__bases_clear_after_half(game_ready):
    g = game_ready
    # batter singles
    batter1 = g.inning.half.batting.up_to_bat
    g.single()
    assert g.bases == [batter1, None, None]
    g.inning.make_next_half()
    assert g.bases == [None, None, None]


def test__base_queue__bases_empty__four_singles(game_ready):
    g = game_ready
    # batter singles
    batter1 = g.inning.half.batting.up_to_bat
    g.single()
    assert g.bases == [batter1, None, None]

    # batter singles, advancing runner at first
    g.inning.half.make_next_at_bat()
    batter2 = g.inning.half.batting.up_to_bat
    g.single()
    assert g.bases == [batter2, batter1, None]

    # batter singles, advancing runners at first and second
    g.inning.half.make_next_at_bat()
    batter3 = g.inning.half.batting.up_to_bat
    g.single()
    assert g.bases == [batter3, batter2, batter1]

    # batter singles, advancing runners at first, second, and third
    g.inning.half.make_next_at_bat()
    batter4 = g.inning.half.batting.up_to_bat
    g.single()
    assert g.bases == [batter4, batter3, batter2]
    assert g.inning.half.runs == 1

def test__base_queue__bases_empty__two_doubles(game_ready):
    g = game_ready
    # batter doubles
    batter1 = g.inning.half.batting.up_to_bat
    g.double()
    assert g.bases == [None, batter1, None]

    # batter doubles, driving home runner at second
    g.inning.half.make_next_at_bat()
    batter2 = g.inning.half.batting.up_to_bat
    g.double()
    assert g.bases == [None, batter2, None]
    assert g.inning.half.runs == 1

def test__base_queue__bases_empty__two_triples(game_ready):
    g = game_ready
    # batter doubles
    batter1 = g.inning.half.batting.up_to_bat
    g.triple()
    assert g.bases == [None, None, batter1]

    # batter triples, driving home runner at third
    g.inning.half.make_next_at_bat()
    batter2 = g.inning.half.batting.up_to_bat
    g.triple()
    assert g.bases == [None, None, batter2]
    assert g.inning.half.runs == 1

def test__base_queue__bases_empty__home_run(game_ready):
    g = game_ready
    # batter homers
    batter1 = g.inning.half.batting.up_to_bat
    g.home_run()
    assert g.bases == [None, None, None]
    assert g.inning.half.runs == 1

def test__base_queue__bases_loaded__home_run(game_ready):
    g = game_ready
    # first three batters single
    for n in range(3):
        g.inning.half.make_next_at_bat()
        g.single()
    # fourth batter hits a dinger
    g.inning.half.make_next_at_bat()
    g.home_run()
    assert g.bases == [None, None, None]
    assert g.inning.half.runs == 4
