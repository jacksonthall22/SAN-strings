import chess
from typing import Literal, Set


_b = chess.Board.empty()
""" A blank `chess.Board` to use for generating moves. """


def get_adjacent_files(file: Literal[0, 1, 2, 3, 4, 5, 6, 7]) -> chess.Bitboard:
    """
    Get a `chess.Bitboard` of `file`'s adjacent files.
    """
    return (chess.BB_FILES[file - 1] if file > 0 else 0) | (
        chess.BB_FILES[file + 1] if file < 7 else 0
    )


def get_adjacent_ranks(rank: Literal[0, 1, 2, 3, 4, 5, 6, 7]) -> chess.Bitboard:
    """
    Get a `chess.Bitboard` of `rank`'s adjacent ranks.
    """
    return (chess.BB_RANKS[rank - 1] if rank > 0 else 0) | (
        chess.BB_RANKS[rank + 1] if rank < 7 else 0
    )


def get_pawn_sans(only_for_color: chess.Color | None = None) -> Set[str]:
    """
    Get all possible SAN strings for pawn moves. If `only_for_color` is
    specified, then only return pawn moves for that color; otherwise return
    pawn moves for both colors.
    """
    sans = set()

    PAWN_OCCUPIABLE = chess.SquareSet(chess.BB_ALL - chess.BB_BACKRANKS)

    w_pawn = chess.Piece.from_symbol("P")
    b_pawn = chess.Piece.from_symbol("p")

    def add_pawn_sans_for_color(color: chess.Color):
        _b.turn = color
        self_pawn = w_pawn if color == chess.WHITE else b_pawn
        other_pawn = b_pawn if color == chess.WHITE else w_pawn

        for from_square in PAWN_OCCUPIABLE:
            _b.clear_board()
            _b.set_piece_at(from_square, self_pawn)
            attacks = _b.attacks(from_square)

            # Set enemy pawns at the diagonal attacked squares
            for s in attacks:
                _b.set_piece_at(s, other_pawn)

            # Now forward moves and the diagonal captures are legal,
            # so we can just add all legal SAN moves
            for move in _b.legal_moves:
                sans.add(_b.san(move))

    if only_for_color in (chess.WHITE, None):
        add_pawn_sans_for_color(chess.WHITE)
    if only_for_color in (chess.BLACK, None):
        add_pawn_sans_for_color(chess.BLACK)

    return sans


def get_piece_sans(symbol: Literal["N", "B", "R", "Q"]) -> Set[str]:
    """
    Get all possible SAN strings for piece types that might require a
    discriminator—namely knights, bishops, rooks, and queens.
    """
    assert symbol in (
        "N",
        "B",
        "R",
        "Q",
    ), f'Invalid piece symbol {symbol}, must be in ("N", "B", "R", "Q")'

    piece = chess.Piece.from_symbol(symbol)
    is_knight = piece.piece_type == chess.KNIGHT
    is_rook = piece.piece_type == chess.ROOK

    sans = set()

    def add_sans(discriminator: str, to_square):
        """
        Add two SAN strings to `sans` for the given `discriminator` and `to_square`:
        one for a non-capturing move and one for a capturing move.
        """
        to_square_name = chess.square_name(to_square)
        for capture in ("", "x"):
            sans.add(f"{symbol}{discriminator}{capture}{to_square_name}")

    for to_square in chess.SQUARES:
        # We always add the un-discriminated move and capturing move
        add_sans("", to_square)

        # For N/B/R/Qs, we can determine whether the piece needs a file discriminator
        # independently based solely on the piece type and the `to_square`. Whether it
        # needs a rank discriminator and/or a full-square discriminator depends also on
        # the `from_square`, which is handled in loops below.
        _b.clear_board()
        _b.set_piece_at(to_square, piece)
        attacks = _b.attacks(to_square)

        # If `piece` is a knight or rook (which always may require a file discriminator)
        # or if two or more non-vertical rays protrude from `to_square` in the direction of
        # `piece`'s movement, we need a file discriminator.
        # Below we do a bitwise AND between `attacks` and `to_square`'s adjacent files.
        # If the resulting int has 2 or more truthy (overlapping) bits, then we could
        # put a `piece` on both of these squares to require a rank discriminator when
        # moving to `to_square`.
        if (
            is_rook
            or is_knight
            or int.bit_count(
                int(attacks) & get_adjacent_files(chess.square_file(to_square))
            )
            >= 2
        ):
            for from_square in attacks:
                discriminator = chess.FILE_NAMES[chess.square_file(from_square)]
                add_sans(discriminator, to_square)

        # If the `piece` is a knight or if two or more non-vertical rays protrude from `to_square`
        # in the direction of the piece's movement, we need to check each `from_square` to see if
        # its file has two or more truthy bits in `attacks` (including itself). If so, we need a
        # rank discriminator.
        if (
            is_knight
            or int.bit_count(
                int(attacks) & get_adjacent_ranks(chess.square_rank(to_square))
            )
            >= 2
        ):
            for from_square in attacks:
                num_file_attacks = int.bit_count(
                    int(attacks) & chess.BB_FILES[chess.square_file(from_square)]
                )
                if num_file_attacks >= 2:
                    discriminator = chess.RANK_NAMES[chess.square_rank(from_square)]
                    add_sans(discriminator, to_square)

        # For all piece types (N/B/R/Qs), we need to check each `from_square` to see if
        # its file and rank both have two or more truthy bits in `attacks` (including itself).
        # If so, we need a full-square discriminator.
        for from_square in attacks:
            num_file_attacks = int.bit_count(
                int(attacks) & chess.BB_FILES[chess.square_file(from_square)]
            )
            num_rank_attacks = int.bit_count(
                int(attacks) & chess.BB_RANKS[chess.square_rank(from_square)]
            )
            if num_file_attacks >= 2 and num_rank_attacks >= 2:
                discriminator = chess.square_name(from_square)
                add_sans(discriminator, to_square)

    return sans


def get_king_sans() -> Set[str]:
    """
    Get all possible SAN strings for king moves.
    """
    sans = set()

    for to_square in chess.SQUARES:
        # Add the capturing and non-capturing SANs
        to_square_name = chess.square_name(to_square)
        sans.add(f"K{to_square_name}")
        sans.add(f"Kx{to_square_name}")

    # Add castling moves
    sans.add("O-O")
    sans.add("O-O-O")

    return sans


def main():
    pawn_sans = get_pawn_sans()
    knight_sans = get_piece_sans("N")
    bishop_sans = get_piece_sans("B")
    rook_sans = get_piece_sans("R")
    queen_sans = get_piece_sans("Q")
    king_sans = get_king_sans()
    all_sans = (
        pawn_sans | knight_sans | bishop_sans | rook_sans | queen_sans | king_sans
    )

    def sort_key(s):
        return (len(s), s)
    
    all_sans = sorted(all_sans, key=sort_key)
    all_sans_with_symbols = sorted(
        [san + symbol for symbol in ("", "+", "#") for san in all_sans], key=sort_key
    )

    with open("san_strings.txt", "w") as f:
        f.write("\n".join(all_sans))

    with open("san_strings_with_symbols.txt", "w") as f:
        f.write("\n".join(all_sans_with_symbols))

    print("Done!")


if __name__ == "__main__":
    main()
