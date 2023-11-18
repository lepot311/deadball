import pytest

from game import Game, roll


def test_retired_player_is_available(empty_team, player):
    empty_team.players.add(player)
    empty_team.lineup.append(player)
    empty_team.retire(player)
    assert empty_team.is_available(player) is False

def test_bench_size(team):
    assert len(team.bench) == 40 - 9

def test_sub_player(team):
    entering = team.get_player_by_number(10)
    leaving  = team.get_player_by_number(1)
    team.sub_player(entering, leaving)
    assert entering in team.lineup
    assert leaving in team.retired
    assert team.is_available(entering) is True
    assert team.is_available(leaving) is False

def test_roll():
    for n in range(10):
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

def test_bullpen(team):
    assert len(team.bullpen) == 10
    assert all([ p.pd for p in team.bullpen ])

def test_lineup(team):
    # lineup requires 9 numbers
    with pytest.raises(AssertionError):
        team.set_lineup(numbers=[1, 2, 3])

    # default to 1-9
    team.set_lineup()

    # set custom order
    team.set_lineup(numbers=[1, 2, 3, 7, 8, 9, 4, 5, 6])

def test_get_team_from_roster():
    game = Game()
    team = game.get_team_from_roster('tests/roster__test_team.csv')
    team.set_lineup()
    assert team.lineup[0].name == 'Winnie'

def test_game_ready__bases_empty(game_ready):
    assert game_ready.bases == [None, None, None]

def test_game_ready__bases_clear(game_ready):
    game_ready.bases.clear()
    assert game_ready.bases == [None, None, None]

def test_base_queue__bases_empty__batter_singles(game_ready):
    g = game_ready
    # advance batter to first
    batter = g.inning.half.batting.up_to_bat
    g.single()
    assert g.bases == [batter, None, None]

def test_base_queue__runner_on_1__batter_singles(game_ready):
    g = game_ready
    # advance batter to first
    batter1 = g.inning.half.batting.up_to_bat
    g.single()
    assert g.bases == [batter1, None, None]

    # advance next batter to first, moving up runner at first to second
    g.inning.half.make_next_at_bat()
    batter2 = g.inning.half.batting.up_to_bat
    g.single()
    assert g.bases == [batter1, batter2, None]
