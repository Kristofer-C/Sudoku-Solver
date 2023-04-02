# Sudoku Solver
Python files and .exe for an app that solves sudoku puzzles up to 36x36.

## Sudoku_Solver.py
This Python script is designed to solve Sudoku puzzles. The way the program solves the puzzles is meant to mimick the approach I use for Sudoku. The user types out the puzzle as a 2D array and the program returns the solved puzzle as a 2D array. As it is right now, it shold be able to solve any size of Sudoku puzzle. I have not tested it extensively so there could be bugs.

### Nomenclature

**Puzzle** - The puzzle refers to the Sudoku puzzle to be solved. It's the big box full of numbers the user sees in their app or the newspaper or something.

**Grid** - The grid, often named `grid` throughout the program, is the 2 dimensional square numpy array that represents the puzzle and is the input to the program. 

**Square** - The puzzle is divided into squares arranged with the same number of squares in each dimension. In the final solution, each square contains one number. 

**Size** - "Size" or `size` is the number of squares along a single side of the puzzle. For a typical 9x9 Sudoku puzzle, the value of this variable is `9`, so puzzles can be described as being of shape `size` by `size`.

**Number** - Numbers refer to the values that populate the squares. Each element in the `grid` is an integer representing the value in the corresponding square of the puzzle. For input and during the solving process, zeros populate the `grid` array in the positions where a square is blank in the puzzle. There are `size` different numbers that populate the squares of the final solution.

**Candidate** - During the solving process, a candidate is a number that has not been eliminated as the possible final solution value for a particular square in the puzzle or grid. The variable `cand` is used to hold the value of a candidate of a square.

**Row** - A row is a set of `size` squares arranged horizontally in the puzzle or grid. In the final solution, each square in a row must contain a different number. The variable `row` is often used to denote the index of the row of interest.

**Column** - A column is a set of `size` squares arranged vertically in the puzzle or grid. The variable `col` is often to denote the index of the column of interest.

**Block** - A block is a set of `size` squares in a section of the puzzle. In a typical 9x9 Sudoku puzzle, they are 3 squares wide and tall, and there are 9 of them in the puzzle. Like rows and columns, blocks are all separate and do not contain any of the same squares. The borders between them are often shown as thicker lines than those that separate all other squares. In the final solution, each block contains one of each number. The variable `block_num` is often used as the index for the block number in the puzzle or grid, starting with 0 for the block in the top left corner and increasing left to right, top to bottom.

**Set** - A general term used to refer to a row, column, or block of squares. A set of squares has the property that each square must contain a different number in the final solution.


### Structure

The whole solving program is bundled as a single Python class called `Sudoku_Puzzle` with functions and puzzle-specific variables that are used throughout. When an object is created with `Sudoku_Puzzle`, a 2D numpy array of the puzzle must be given as an argument, as well as the width of the blocks if it is not a standard 9x9 puzzle. The provided array is used to initialize the value for the `grid` attribute. The `size` attribute is determined from the shape of `grid`.

A second array is initialized as an attribute called `cands`. `cands` is a 3D numpy array with a length of `size` in each dimension. `cands` contains a list of candidates for each square in the puzzle. The candidate lists are always of length `size` and contain 1s and 0s. A candidate list contains 1s in the positions whose indeces are one less than the candidate numbers for its corresponding square (because Python indexing starts at zero) and 0s in all other positions. For example, if a sqaure has a possible final value solution of 1, 3, or 8, the `cand` list for that square would be `[1,0,1,0,0,0,0,1,0]`.

The solving process iteratively uses a set of logical rules operating with information in `grid` and `cands` to eliminate candidates and populate `grid` with solved numbers. Once the object is created with a given input array, the `solve_loop()` method can be called to solve the Sudoku puzzle. Currently, print statements printing out which logical rule is being employed at every step and other messages have been commented out for compatibility with the GUI file. When the loop is complete, the `grid` attribute can be printed to view the solved (or unfinished) puzzle as an array of numbers.

### Strategy

The `solve_loop()` method works iteratively to eliminate candidates and fill in solved values based on the current state of `grid` and `cands`. In the first stage of each iteration, a set of logical rules are employed to eliminate candidates, using progressively more computationally intensive rules until a change can be made, then the `solve_step()` method is used to fill in solved values. 

#### Solve step
`solve_step()` changes the value of a square in `grid` from a zero to a solved number if one of two conditions is met:

1 - The square has only one candidate, in which case that candidate becomes the solved number for that square.

2 - The square is the only one in its row, column, or block with a candidate for that number, in which case that candidate becomes the solved number for that square.

#### The Rules

I have intentified a small set of logically distinct rules that I used when solving Sudoku puzzles. I have translated them into Python code and they are used to eliminate candidates. They are named and described as follows:

**Rule 0**: All candidates are eliminated from squares that contain solved numbers, and candidates of a number are eliminated from squares in the sets containing a square with that solved number. Rule 0 is the only rule that looks at the values in `grid`.

**Rule 1**: Candidates of a number are eliminated from squares in a set when a group of squares in that set contain candidates for that number and are the only squares containing candidates for that number in a different set. For example, if two squares in a block are the only ones with candidates for 9 and those squares are in the same row, then candidates for 9 are eliminated from all the other squares in that row.

"Applying Rule 1 to a set" means checking that set for a candidate value that only appears in squares that are a part of another set. 

**Rule 2**: Rule 2 can be thought of as eliminating candidates based on two different conditions:
1. If there is a group of $n$ squares in a set containing only candidates from a group of $n$ numbers, then those candidates are removed from the rest of the squres in the set. For example, If three squares in a block contain candidates only for some combination of 1, 8, and 9, then 1, 8, and 9, are eliminated from all the other squares in the block. This condition is more commonly found with pairs.
2. If there is a group of $n$ numbers that only appear as candidates in a group of $n$ squares in a set, then all the other candidates may be removed from that group of squares. For example, if the numbers 2 and 7 are candidates in only two squares in a given row, then the candidates for all the other numbers can be removed from the two squares with 2 and 7 as candidates.

If either condition is met, the result in two self-contained groups of squares and candidates in a set. It turns out that if condition 1 is met for a group of $n$ squares and numbers in a set with $m$ solved squares, then condition 2 must be true for the other $size - n - m$ squares and numbers in the set. This equivalency means that if both conditions are checked, then the maximum group size that needs to be looked for is $(size - m)//2$. As well, since condition 1 removes candidates from groups of squares and condition 2 removes squares from groups of candidate numbers, the logic applied is the same. The same set can be checked for both conditions by transposing the set of candidate lists and applying the same logic, which is how Rule 2 is implemented in the program.

*Furthermore*, when Rule 2 is applied to a slice of the `cands` array corresponding to a particular number, it functions as what is referred to as the X-wing strategy. The transpose in this case checks for the X-wing condition in rows and columns.

**Rule 3**: Rule 3 eliminates candidates based on what is referred to as the Y-wing strategy. Look it up lol.

**Rule 4**: If I'm solving a Sudoku puzzle and none of the above rules can eliminate candidates, I have another strategy that involves looking at chains of candidates around the grid and recognizing when they don't "loop around properly," but I don't even want to try to code that in. So Rule 4 just guesses, which is usually sufficient at this point anyway. My strategy is only a small shortcut for guessing anyway. Rule 4 picks a square with two candidates and tries eliminating one. If it can solve the grid properly with that change, then it is solved. If not, it goes back to the state of `grid` and `cands` before it guessed and tries eliminating the other candidate in that square. If that doesn't work, it moves to the next square with two candidates and repeats until both candidates in every two-candidate-containing square have been tried. In theory. I haven't tested this functionality.

In each iteration of the solve loop, the rules are employed in increasing order of computational complexity until one or more candidates are able to be eliminated. The most complex rule that needed to be used to solve a puzzle (along with the number of calls to `solve_step`, stored in the attribute `num_steps`) is my metric for the difficulty of a puzzle. I was surprised to find that every hardest-difficulty 9x9 puzzle I looked for could be solved by only going up to Rule 2. 

### Lack of optimization

This solver is very inefficient. A human puzzler would know to only consider squares that have changed candidates as a result of a recent logic rule when looking to make another change, or they would only consider the squares that could possibly be affect by the change. They would also know which rules are worth checking with depending on the change. Instead, this program checks every square with every rule whenever a single change is made. Another example is when applying Rule 1 to blocks, it only needs to check for the presence of `block_h` candidates of a number when checking if they're all in the same column and `block_w` candidates of a number when checking if they're all in the same row, but the way it's written just checks rows and columns for the larger of `block_w` and `block_h`.

I'm okay with this. The goal of this project is to be a fun exercise to see if if I can write the algorithms I used in my head. I have no interest in optimization, and frankly, my laptop has been able to solve these 9x9 puzzles pretty much instantly. If I wanted to conquer puzzles up to 1000x1000, then I'd start to worry. But there's no reason for this auxillary problem to become my entire life.

### Possible bugs

This program hasn't been tested super thoroughly. My first guess for any bug that's discovered is a slicing error that just haven't come up because the program was able to solve the puzzle anyway. Related: it could be an assignment error where I thought I was assigning a set of values to a slice of `cands` but it's actually just a copy of a slice and not a view.


## Sudoku_Solver_GUI.py
This is the python script used to make a user interface for using the Sudoku_Solver.py program. It is based on the Tkinter module.

At the top of the interface page is the grid of entry widgets into which the user inputs the numbers from the Sudoku puzzle. Pressing `Enter` or clicking the `Solve` button will take the inputs as a grid, run the Sudoku_Solver program with it, and display the (solved) result in the entry widget grid. All of the error checking occurs before the grid is fed to the solver, and various messages will be displayed beneath the buttons if anything is not right with the inputs given by the user. If the puzzle is solved successfully, the program will display the number of steps and the most complex Rule used to solve it. 

Pressing `Reset` will delete the entries made by the solver, reverting the entry widget grid to wht the user inputted before giving the command to solve.

Pressing `Clear` will delete all the numbers from the entries, restoring the grid to a blank state.

The user may also change the size of the entry widget grid by entering a custom size and block width into the corresponding fields and pressing `Change size`. Error/compatibility checking is also performed here before making any changes. 

### Notes
In principle, the Sudoku_Solver.py program can handle any size of Sudoku puzzle. However, I only made a number map allowing user inputs up to "AA", corresponding to a Sudoku puzzle size of 36x36. I also didn't bother shrinking the entry widget grid according to the size of of the puzzle, so a 36x36 grid would already be enormous on the screen. Finally, because the solving program isn't very optimized, I don't know how well it would handle larger puzzles.

The whole app and especially the entry grid look bland and ugly. Grid lines between the entry widgets (like in a real-life Sudoku puzzle) would be an enormous improvement, but I couldn't figure out how to implement that. A possible future direction would be to make this a webpage, in which case I think there is more cosmetic control more readily available.
