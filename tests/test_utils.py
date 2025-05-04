import pytest

from ytm2lfm.utils import find_overlap_start_index


@pytest.mark.parametrize(
    "history_list, scrobbled_list, min_overlap_length, expected",
    [
        # must return 1 because there's only one new element which is "c"
        (["c", "e", "d", "b", "a"], ["e", "d", "c", "b", "a"], 2, 1),
        # repeat same last music return 0
        (["e", "d", "c", "b", "a"], ["e", "d", "c", "b", "a"], 2, 0),
        # play two musics from past. return 2
        (["a", "b", "e", "d", "c"], ["e", "d", "c", "b", "a"], 2, 2),
        # play two musics from past. return 2
        (["b", "a", "e", "d", "c"], ["e", "d", "c", "b", "a"], 2, 2),
        # play two new musics. return 2
        (["f", "g", "e", "d", "c"], ["e", "d", "c", "b", "a"], 2, 2),
        # didn't match any pattern. return -1
        (["f", "g", "h", "i", "j"], ["e", "d", "c", "b", "a"], 2, None),
        # matched pattern. return 5
        (["f", "g", "h", "i", "j", "e", "d"], ["e", "d", "c", "b", "a"], 2, 5),
        # didn't match pattern long enough: threshold is 3, matched sequence of 2. return -1
        (["f", "g", "h", "i", "j", "e", "d"], ["e", "d", "c", "b", "a"], 3, None),
        # invalid input, empty lists
        ([], [], 3, None),
        (["e", "d"], [], 3, None),
        ([], ["f", "g"], 3, None),
        (["c", "e", "d", "b", "a"], ["e", "d", "c", "b", "a"], 0, None),
    ],
)
def test_find_overlap_start_index(history_list, scrobbled_list, min_overlap_length, expected):
    assert find_overlap_start_index(history_list, scrobbled_list, min_overlap_length) == expected
