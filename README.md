# SAN Strings

This simple script generates all **37,302** possible [Standard Algebraic Notation (SAN)](https://en.wikipedia.org/wiki/Algebraic_notation_(chess)#:~:text=Algebraic%20notation%20(or%20AN)%20is,books%2C%20magazines%2C%20and%20newspapers.) strings for chess moves, with some special logic to
avoid listing SAN strings that can never actually occur for geometric reasons.

If someone notices a mistake in my logic (that some strings generated can never occur), please open an issue!

### Note
Check (`+`) and checkmate (`#`) symbols are omitted in `san_strings.txt` but included in `san_strings_with_symbols.txt`. It is fairly easy 
to convince yourself that no special logic is required to determine which subset of all SAN moves could deliver check/mate: all moves can 
deliver either check or mate at least via a discovery. Therefore, `san_strings_with_symbols.txt` (37,302 lines) is exactly three times the length of 
`san_strings.txt` (12,434 lines) as it simply makes two additional copies of each SAN move, one appending `+` and one appending `#`.

# Run it yourself
```sh
git clone https://github.com/jacksonthall22/SAN-strings.git && cd SAN-strings
pip install -r requirements.txt
python3 gen_san_strings.py
```

# How it works
## Discriminators

The only considerations beyond the naive approach of "move every piece from every square to every other legal square" has to do
with discriminators: some are legal syntactically but could never occur. The logic is slightly different for each piece, which
I describe below.

### Bishops
Bishops are the most complicated. For example, in the rare situation where a promotion to a bishop leaves two same-colored
bishops on the board, a bishop move to ranks `1` or `8` can require a discriminator, but will never require a rank discriminator
(ex. `B3d1`). At most two diagonal rays protrude from the destination square, and only one bishop occupying each diagonal
could ever move to that square. Since the two bishops will never be on the same file, we can fully disambiguate the move
using only the file of the source piece (ex. `Bcd1`). Although specifying only the rank is sometimes also sufficient, [the 
file will always be preferred](https://en.wikipedia.org/wiki/Algebraic_notation_(chess)#Disambiguating_moves).

![image](https://backscattering.de/web-boardimage/board.svg?size=400&coordinates=true&fen=8/8/8/8/6B1/1B6/8/8&arrows=Gb3d1,Gd1)

Similarly, a bishop moving to the corner never requires a discriminator, since only one diagonal ray protrudes
from the destination square and you can't jump your own pieces.

![image](https://backscattering.de/web-boardimage/board.svg?size=400&coordinates=true&fen=8/8/8/8/4B3/5B2/8/8&arrows=Ge4a8)

Bishops moving to `a2-a7` or `h2-h7` require three special cases corresponding to the following three sets of squares that the bishop is landing on:
- `a2`/`a7`/`h2`/`h7`
- `a3`/`a6`/`h3`/`h6`
- `a4`/`a5`/`h4`/`h5`

![image](https://backscattering.de/web-boardimage/board.svg?size=300&coordinates=true&fen=8/8/8/8/8/8/8/8&arrows=a2,a7,h2,h7) ![image](https://backscattering.de/web-boardimage/board.svg?size=300&coordinates=true&fen=8/8/8/8/8/8/8/8&arrows=a3,a6,h3,h6) ![image](https://backscattering.de/web-boardimage/board.svg?size=300&coordinates=true&fen=8/8/8/8/8/8/8/8&arrows=a4,a5,h4,h5)

These moves can always be disambiguated using the rank, and sometimes the file, by the same logic as above. However, since using the file
is prefered over the rank when available in SAN syntax, we *only sometimes* must generate both, ex. `Beh6` and `B4h6`:

![image](https://backscattering.de/web-boardimage/board.svg?size=400&coordinates=true&fen=8/6B1/8/8/5B2/8/8/8&arrows=Gf4h6,h6,Bf1f8) ![image](https://backscattering.de/web-boardimage/board.svg?size=400&coordinates=true&fen=5B2/8/8/8/5B2/8/8/8&arrows=Gf4h6,h6,Ba4h4)

However, for example, the "valid" SAN string `B3h6` is not possible. The presence of a rank discriminator implies that using the file
would not have been enough to fully disambiguate the source piece (since using the file is preferred). Therefore, we know the following:
- There is a bishop on rank `3` rank that can move to `h6`. The only square where this is possible is `e3`.
- There must be another bishops on the same file as the source bishop (the `e` file), since otherwise the source file would have been
the disambiguator.

but these facts already make a contradiction. It is also visually not possible—we would need an `e9` square to put another bishop on 
the `e` file that can move to `h6`:

![image](https://backscattering.de/web-boardimage/board.svg?size=400&coordinates=true&fen=5B2/8/8/8/8/4B3/8/8&arrows=Ge3h6,h6,Rh6f8)

The general rule is that we always generate a string for the file discriminator, but only generate one for the rank discriminator 
if the rank of the source piece is within *d* ranks of the destination piece, where *d* is the length of the shortest diagonal protruding
from the destination square:

![image](https://backscattering.de/web-boardimage/board.svg?size=300&coordinates=true&fen=6B1/8/6B1/8/8/8/8/8&arrows=Bh7g8,h7,Bh7g6,Gh8a8,h7a7,h6a6,Rh5a5,Rh4a4,Rh3a3,Rh2a2,Rh1a1) ![image](https://backscattering.de/web-boardimage/board.svg?size=300&coordinates=true&fen=5B2/8/8/8/5B2/8/8/8&arrows=Bh6f8,h6,Bh6f4,Gh8a8,h7a7,h6a6,h5a5,h4a4,Rh3a3,Rh2a2,Rh1a1) ![image](https://backscattering.de/web-boardimage/board.svg?size=300&coordinates=true&fen=4B3/8/8/8/8/8/4B3/8&arrows=Bh5e8,h5,Bh5e2,Gh8a8,h7a7,h6a6,h5a5,h4a4,h3a3,h2a2,Rh1a1)

### Rooks
Rooks are more straighforward. Their only restriction on discriminators is that if a rook is landing on ranks `1` or `8`, it will never require 
a rank discriminator. If two rooks can move to the same backrank destination square, they must not be on the same file, so the file will always be
the preferred discriminator. Therefore a full-square discriminator will never be required for these moves either.

![image](https://backscattering.de/web-boardimage/board.svg?size=400&coordinates=true&fen=R6R/8/8/8/8/8/5R2/5R2&arrows=f8,a8f8,h8f8,f2f8,Rf1)

The same is not true of the `a` and `h` files, which can require a file, rank, or full-square discriminator.

![image](https://backscattering.de/web-boardimage/board.svg?size=400&coordinates=true&fen=7R/8/RR6/8/8/8/8/7R&arrows=h6,b6h6,h1h6,h8h6)

### Knights
Knights moving to ranks 1 or 8 never require a rank or full-square descriminator since the knights that can move there are never on the same file.

![image](https://backscattering.de/web-boardimage/board.svg?size=400&coordinates=true&fen=8/2N3N1/1N3N2/8/8/8/8/8&arrows=b6a8,c7a8,Bc7e8,Bd6e8,Bf6e8,Bg7e8)

### Queens
Queens have no restrictions because at least three rays protrude from each square in the directions of the queen's movement, so we can always
construct a scenario where a file, rank, or full-square disambiguator is necessary.

![image](https://backscattering.de/web-boardimage/board.svg?size=400&coordinates=true&fen=8/3Q4/8/8/8/3Q3Q/8/8&arrows=d3h7,h7)

### Pawns
Pawns have no restrictions. We just have to be sure not to double-count the same strings, since for example the pawn moves `a2a4`/`a3a4`
(by white) and `a5a4` (by black) would all be notated in SAN as `a4`.
