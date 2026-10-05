# Preface

> **A drunk man always finds his way home;**
> **A drunk bird, nevertheless, may not.**
> **A drunken emu, thankfully though,**
> **Almost surely still gets home.**
>
> — after Shizuo Kakutani, on Pólya's theorem

Pólya proved it in 1921: a simple random walk on ℤ^d returns to where it started
with probability 1 when *d* ≤ 2, and has a positive chance of never coming back
when *d* ≥ 3. The man staggers around a town, which is a plane, and the plane
brings him home. The bird has a third axis and loses it.

Note what the second line does *not* say. Not *will be lost* — **may not**. It
is a statement about possibility, and it leaves the bird's case open where the
commoner telling closes it.

Which matters, because of one fact about this particular bird.

**An emu cannot fly.**

So the sentence never settles, and that is the better half of the joke.
Kakutani's bird has three axes and the odds are against it; an emu has two and
the odds are certain. Whether a drunken emu is the bird that gets home or the
bird that doesn't depends entirely on whether you were thinking about the wings
or the walking — and both readings are true while saying opposite things.

Read it the second way. A drunken emu is a bird confined to *d* = 2. It weaves,
it doubles back, it takes an absurd number of steps to cover ground a sober
walker would cross in a straight line — and it is *recurrent*. It gets home. Not
because it aimed there, and not quickly, but because the plane it is stuck on
does not let it do anything else.

*Almost surely* is not hedging. It is the term of art for probability 1, and it
is the only phrase in English that means **certain** while sounding like a
person who would rather not commit. Which is the right register for a tool whose
job is saying how much it actually knows.

That is the property you want in a reader simulator. An eye that will not hold
still is not an eye that is lost. It lands somewhere in the middle, skips ahead,
slides off a wall of text, doubles back, and given enough passes it does reach
everything on the page. What a layout owes it is not a straight line. It is that
every return should land on something worth having found.

So the tests here do not assume a reader who starts at the top left and proceeds
in order. They assume a walk. `reading.py` measures what that walk costs:
whether a phrase has to be read twice for no new information, whether a colour
means something only six hundred pixels away, how far down the first useful
thing sits. The staggering is not the failure mode being tested for.

It is the reader.

---

*Pólya, G. (1921). "Über eine Aufgabe der Wahrscheinlichkeitsrechnung betreffend
die Irrfahrt im Straßennetz", Mathematische Annalen 84, 149–160.*

*The remark survives only as a retelling and the wording drifts. MacTutor and
Durrett's* Probability: Theory and Examples *(5th ed., 2019) both give "may get
lost forever"; Herdade & Vu's* Tipsy cop and tipsy robber *(arXiv:2208.12829)
reports it as delivered in a talk — "a drunk man will always find his way home,
but a drunk bird may not". The last is the version above, chosen because it is
the one that stays undecided.*
