import chess
from typing import Set


_b = chess.Board.empty()
def get_squareset(from_square: chess.Square, symbol: str) -> chess.SquareSet:
    """
    Get a ``chess.SquareSet`` of all squares that the piece could move to.
    ``SquareSet``s for pawns contain all squares where a white OR black pawn
    could move to (including captures in both directions).
    """
    destinations = chess.SquareSet()
    
    # For non-pawns, this is sufficient
    _b.clear_board()
    _b.set_piece_at(from_square, chess.Piece.from_symbol(symbol))
    for sq in _b.attacks(from_square):
        destinations.add(sq)

    # For pawns, manually add other-color pawn capture directions,
    # and non-capture movement squares
    if symbol == 'p':
        destinations |= get_squareset(from_square, 'P')

        file, rank = chess.square_name(from_square)
        destinations.add(chess.parse_square(file + str(int(rank) - 1)))
        destinations.add(chess.parse_square(file + str(int(rank) + 1)))
        if rank == '2':
            destinations.add(chess.parse_square(file + str(int(rank) + 2)))
        elif rank == '7':
            destinations.add(chess.parse_square(file + str(int(rank) - 2)))

    return destinations


CORNERS_SQUARESET = chess.SquareSet(chess.BB_CORNERS)
BACKRANKS_SQUARESET = chess.SquareSet(chess.BB_BACKRANKS)
EDGES_SQUARESET = chess.SquareSet(chess.BB_BACKRANKS | chess.BB_FILES[0] | chess.BB_FILES[7])

# Special cases for bishop SAN moves with rank disambiguators
EDGE_2_SQUARESET = chess.SquareSet(chess.BB_A2 | chess.BB_A7 | chess.BB_H2 | chess.BB_H7)
EDGE_3_SQUARESET = chess.SquareSet(chess.BB_A3 | chess.BB_A6 | chess.BB_H3 | chess.BB_H6)
EDGE_4_SQUARESET = chess.SquareSet(chess.BB_A4 | chess.BB_A5 | chess.BB_H4 | chess.BB_H5)

san_strings: Set[str] = set()
for from_square in chess.SQUARES:
    from_square_name = chess.square_name(from_square)
    from_file, from_rank = from_square_name

    PIECE_SYMBOLS = chess.PIECE_SYMBOLS[1:] if from_rank not in ('1', '8') else chess.PIECE_SYMBOLS[2:]
    piece_destinations = {symbol: get_squareset(from_square, symbol) for symbol in PIECE_SYMBOLS}
    for symbol, to_squares in piece_destinations.items():
        for to_square in to_squares:
            to_square_name = chess.square_name(to_square)
            to_file, to_rank = to_square_name

            if symbol == 'p':
                if from_file == to_file:
                    # Non-capture
                    san = to_square_name
                else:
                    # Capture
                    san = f'{from_file}x{to_square_name}'

                # Promotions
                if to_rank in ('1', '8'):
                    san_strings |= {
                        f'{san}=N',
                        f'{san}=B',
                        f'{san}=R',
                        f'{san}=Q'
                    }
                else:
                    san_strings.add(san)
            elif symbol == 'n':
                if to_square in BACKRANKS_SQUARESET:
                    # Knights moving to ranks 1 or 8 will never be disambiguated by rank or full square
                    san_strings |= {
                        f'N{to_square_name}',
                        f'N{from_file}{to_square_name}',
                        f'Nx{to_square_name}',
                        f'N{from_file}x{to_square_name}',
                    }
                else:
                    san_strings |= {
                        f'N{to_square_name}',
                        f'N{from_file}{to_square_name}',
                        f'N{from_rank}{to_square_name}',
                        f'N{from_square_name}{to_square_name}',
                        f'Nx{to_square_name}',
                        f'N{from_file}x{to_square_name}',
                        f'N{from_rank}x{to_square_name}',
                        f'N{from_square_name}x{to_square_name}',
                    }
            elif symbol == 'b':
                if to_square in CORNERS_SQUARESET:
                    # Bishops moving to the corners will never require any disambiguator
                    san_strings.add(f'B{to_square_name}')
                elif to_square in BACKRANKS_SQUARESET:
                    # Bishops moving to ranks 1 or 8 will never be disambiguator by rank or full square
                    san_strings |= {
                        f'B{to_square_name}',
                        f'B{from_file}{to_square_name}',
                        f'Bx{to_square_name}',
                        f'B{from_file}x{to_square_name}',
                    }
                elif to_square in EDGES_SQUARESET:
                    san_strings |= {
                        f'B{to_square_name}',
                        f'B{from_file}{to_square_name}',
                        f'Bx{to_square_name}',
                        f'B{from_file}x{to_square_name}',
                    }

                    # Bishops moving to a2-a7 or h2-h7 require 3 special cases (see README)
                    # Get the length of the shortest diagonal protruding from ``to_square``
                    if to_square in EDGE_2_SQUARESET:
                        shortest_diag_len = 1
                    elif to_square in EDGE_3_SQUARESET:
                        shortest_diag_len = 2
                    elif to_square in EDGE_4_SQUARESET:
                        shortest_diag_len = 3
                    else:
                        raise RuntimeError('This should not happen')

                    # For a rank descriminator to be possible, source and destination square
                    # must be separated by <= ``shortest_diag_len`` ranks
                    if abs(int(to_rank) - int(from_rank)) <= shortest_diag_len:
                        san_strings |= {
                            f'B{from_rank}{to_square_name}',
                            f'B{from_rank}x{to_square_name}',
                        }
                else:
                    san_strings |= {
                        f'B{to_square_name}',
                        f'B{from_file}{to_square_name}',
                        f'B{from_rank}{to_square_name}',
                        f'B{from_square_name}{to_square_name}',
                        f'Bx{to_square_name}',
                        f'B{from_file}x{to_square_name}',
                        f'B{from_rank}x{to_square_name}',
                        f'B{from_square_name}x{to_square_name}',
                    }
            elif symbol == 'r':
                if to_square in BACKRANKS_SQUARESET:
                    # Rooks moving to ranks 1 or 8 will never be discriminated by rank or full square
                    san_strings |= {
                        f'R{to_square_name}',
                        f'R{from_file}{to_square_name}',
                        f'Rx{to_square_name}',
                        f'R{from_file}x{to_square_name}',
                    }
                else:
                    san_strings |= {
                        f'R{to_square_name}',
                        f'R{from_file}{to_square_name}',
                        f'R{from_rank}{to_square_name}',
                        f'R{from_square_name}{to_square_name}',
                        f'Rx{to_square_name}',
                        f'R{from_file}x{to_square_name}',
                        f'R{from_rank}x{to_square_name}',
                        f'R{from_square_name}x{to_square_name}',
                    }
            elif symbol == 'q':
                san_strings |= {
                    f'Q{to_square_name}',
                    f'Q{from_file}{to_square_name}',
                    f'Q{from_rank}{to_square_name}',
                    f'Q{from_square_name}{to_square_name}',
                    f'Qx{to_square_name}',
                    f'Q{from_file}x{to_square_name}',
                    f'Q{from_rank}x{to_square_name}',
                    f'Q{from_square_name}x{to_square_name}',
                }
            elif symbol == 'k':
                # Kings will never require disambiguator
                san_strings |= {
                    f'K{to_square_name}',
                    f'Kx{to_square_name}',
                }
            else:
                raise ValueError(f'bad symbol: {symbol}')

with open('san_strings.txt', 'w') as f:
    f.write('\n'.join(sorted(san_strings, key=lambda s: (len(s), s))))

print('Done!')
