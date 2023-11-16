import pytest


def test_retired_player_is_available(empty_team, player):
    empty_team.players.add(player)
    empty_team.lineup.append(player)
    empty_team.retire(player)
    assert empty_team.is_available(player) is False

def test_bench_size(team):
    assert len(team.bench) == 40 - 9
