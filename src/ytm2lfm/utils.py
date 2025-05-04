# scrobbler/utils.py
from collections import OrderedDict
from typing import List, Optional


def find_overlap_start_index(
    history_list: List[str], scrobbled_list: List[str], min_overlap_length: int
) -> Optional[int]:
    """
    Find the starting index in history_list where it begins to overlap with scrobbled_list.

    This function identifies the point at which the history begins to contain already scrobbled
    tracks. In YouTube Music scrobbling context, this means:
    - Elements before this index are new tracks that need to be scrobbled
    - Elements at and after this index are tracks that have already been scrobbled

    Args:
        history_list: List of track identifiers from recent history (e.g., YouTube Music)
        scrobbled_list: List of already scrobbled track identifiers (from database)
        min_overlap_length: Minimum number of consecutive matching tracks required to
                            confirm a genuine overlap (rather than coincidental matches)

    Returns:
        The index in history_list where overlap with scrobbled_list begins, or
        None if no significant overlap is found (meaning all tracks are new)

    Example:
        history   = [A, B, C, D, E, F, G]
        scrobbled = [D, E, F, G, H, I]
        With min_overlap_length = 3, the function would return 3 (index of 'D' in history).
        This means tracks A, B, C are new and should be scrobbled.
    """
    if not scrobbled_list or not history_list or min_overlap_length <= 0:
        return None

    count = 0
    start_idx = None

    scrobbled_od = OrderedDict.fromkeys(scrobbled_list)

    for idx in range(len(history_list)):
        if history_list[idx] == next(iter(scrobbled_od)):
            if start_idx is None:
                start_idx = idx
            count += 1
        else:
            count, start_idx = 0, None

        if count >= min_overlap_length:
            return start_idx

        scrobbled_od.pop(history_list[idx], None)

    return None
