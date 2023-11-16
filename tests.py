import pytest

from game import roll


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
    for n in range(100):
        assert 0 < roll('d4') < 5
        assert 0 < roll('d8') < 9
        assert 0 < roll('d10') < 11
        assert 0 < roll('d12') < 13
        assert 0 < roll('d20') < 21
        assert 0 < roll('d100') < 101

        assert 0 < roll('1d4') < 5
        assert 1 < roll('2d4') < 9
        assert 3 < roll('4d4') < 17
        assert 1 < roll('2d10') < 21

def test_bullpen(team):
    assert len(team.bullpen) == 10
    assert all([ p.pd for p in team.bullpen ])
