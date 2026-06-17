import pytest

from app.services.player_stats_service import sort_player_stats


def test_sort_player_stats_by_goals():
    players = [
        {"player_name": "Player B", "goals": 1, "assists": 3, "minutes_played": 90},
        {"player_name": "Player A", "goals": 3, "assists": 0, "minutes_played": 80},
        {"player_name": "Player C", "goals": 2, "assists": 1, "minutes_played": 85},
    ]

    sorted_players = sort_player_stats(players, sort_by="goals")

    assert [player["player_name"] for player in sorted_players] == [
        "Player A",
        "Player C",
        "Player B",
    ]


def test_sort_player_stats_by_assists():
    players = [
        {"player_name": "Player B", "goals": 1, "assists": 3, "minutes_played": 90},
        {"player_name": "Player A", "goals": 3, "assists": 0, "minutes_played": 80},
        {"player_name": "Player C", "goals": 2, "assists": 1, "minutes_played": 85},
    ]

    sorted_players = sort_player_stats(players, sort_by="assists")

    assert [player["player_name"] for player in sorted_players] == [
        "Player B",
        "Player C",
        "Player A",
    ]


def test_sort_player_stats_respects_limit():
    players = [
        {"player_name": "Player A", "goals": 3},
        {"player_name": "Player B", "goals": 2},
        {"player_name": "Player C", "goals": 1},
    ]

    sorted_players = sort_player_stats(players, sort_by="goals", limit=2)

    assert len(sorted_players) == 2
    assert [player["player_name"] for player in sorted_players] == [
        "Player A",
        "Player B",
    ]


def test_sort_player_stats_rejects_unknown_sort_field():
    with pytest.raises(ValueError, match="Unsupported player stats sort field"):
        sort_player_stats([], sort_by="unknown")
