import itertools as it
import numpy as np



class Sudoku_Puzzle:
# Define the Sudoku Puzzle object with all the variables and functions
# used to solve the puzzle
   
    def __init__(self, grid=np.zeros((9,9)), block_w=3):
        # Check and initialize parameters and variables used in the solving process.
        # The grid containing the puzzle values and the number of squares in the
        # width of each block should be given when the object is created.
        
        self.grid=np.array(grid).copy() # The 2x2 array containing the starting values from the puzzle
        self.size=self.grid.shape[0] # The side length of the grid and the number of numbers
        self.block_w=block_w
        
       
        # Only the width needs to be entered because the dimensions of the blocks
        # are constrained such that the product is the grid size.
        # Initialize the block height.
        self.block_h=self.size//self.block_w
        
        self.inds=np.arange(self.size) # A list of nummbers up to self.size. Commonly used.            
            
        # Create grids with elements containg the row, column, or block number for each square.
        # Used for slicing out a row or block from cands or with just the row/block number.
        self.row_nums=np.zeros((self.size, self.size))
        self.col_nums=np.zeros((self.size, self.size))
        self.block_nums=np.zeros((self.size, self.size))
        for i in range(self.size):
            self.row_nums[i]=i
            self.col_nums[:,i]=i
            self.block_nums[self.block_h*(i//self.block_h):self.block_h*(i//self.block_h+1),\
                            self.block_w*(i%self.block_h):self.block_w*(i%self.block_h+1)]=i
            
            
        # Initialize candidates
        self.cands=np.ones((self.size,self.size,self.size))
        self.prev_cands=self.cands.copy()

        # Initialize variables for Rule 4
        self.rule_4_count=0 # The number of times Rule 4 has been called
        self.current_cands=self.cands.copy() # The state of cands before Rule 4 was called the first time
        self.current_grid=self.grid.copy() # The state of grid before Rule 4 was called the first time
        self.guess_row=0 # The row index of the current square used for guessing
        self.guess_col=0 # The column index of the current square used for guessing
        self.guess_nums=np.zeros((2)) # The candidates of the current square used for guessing
        # The lists of rows and columns for squares containing two candidates
        self.pairs_rows, self.pairs_cols = np.array([]), np.array([]) 
        
        # Initialize a counter for the number of solve steps taken to solve the puzzle 
        self.num_steps=0
        # Keep track of the highest level Rule needed to solve the puzzle
        self.max_rule=0        
        # Initialize the state of being solved
        self.solved=False
        
        # Create a list of the Rule functions
        self.rule_func_list=[self.Rule_0, 
                             self.Rule_1,
                             self.Rule_2,
                             self.Rule_3,
                             self.Rule_4]
                
    
    def Block_num(self, i, j):
        # Calculates the block number of a square based on its row and column number
        
        return self.block_h*(i//self.block_h)+j//self.block_w

    
    def Rule_0(self):
        # Applies Rule 0 to the entire grid.
        # Rule 0: Eliminate candidates of squares if there is already a square in that 
        # row, column, or block with a solved number

        for i in range(self.size):
            for j in range(self.size):

                num=self.grid[i,j]

                # If the sqaure already has a value, there are no other potential candidates
                if num!=0:
                    self.cands[i,j,:]=0 # set all candidate values to zero

                else:
                    # Isolate the other values currently in the sqaure's row, column, and block
                    row=self.grid[i]
                    col=self.grid[:,j]
                    block=self.grid[self.block_nums==self.Block_num(i, j)]

                    # The different numbers in the row, column, and block
                    # is the list of candidates to remove from that square
                    notslist=np.unique(np.concatenate([row,col,block]))
                    # Zero represents a blank square so it doesn't need to be removed
                    # as a candidate
                    notslist=notslist[notslist!=0]

                    # Set the cadidate list to zero in the position corresponding to the value
                    # already in that row, column, or block
                    if notslist.size>0:
                        self.cands[i,j,notslist-1]=0
                    
    
    
    def Rule_1_columns(self, transpose=False):
        # Applies Rule 1 to all the columns the entire grid
        # Nearly the same code is used to apply Rule 1 to all the rows, 
        # so the transpose of the cands array can be used with the same function.
        
        # When the blocks aren't square, the simple transpose isn't enough
        # to be able to use the exact same code for columns and rows
        # so the 'width' and 'height' of the blocks need to be swapped
        if transpose:
            w=self.block_h
            h=self.block_w
        else:
            w=self.block_w
            h=self.block_h

    
        colsum=self.cands.sum(axis=0) # Sum the candidates along the columns
        colsumbool=np.logical_and(colsum<=h, colsum>1) # Find the sums that are less than or equal to the
            # number of squares in the height of each block
        cols, nums= np.where(colsumbool) # Find the columns in which it occurs and what the corresponding numbers are
        # Find the row numbers for which squares are part of candidate groups
        inds, rows = self.cands[:, cols, nums].T.nonzero() 
        
        # Loop over every instance of there being h or fewer candidates of a number in the same column
        for i in range(len(cols)): 

            # The slice of elements in rows that correspond to the squares in cols that share a candidate
            rows_slice=rows[inds==i] 
            rows_slice_blockn=rows_slice//h # Divided by the block height to get the "block number" in that row

            # The block number of the first entry
            row_blockn=rows_slice_blockn[0]
            
            # If the squares sharing candidates in the column are all in the same block:
            if(rows_slice_blockn==row_blockn).all(): 

                col=cols[i] # The current column
                col_blockn=col//w # The column number divided by the block width to get the "block number" in that column

                # Set all candidates for that value in that block equal to zero
                self.cands[h*row_blockn:h*(row_blockn+1), w*col_blockn:w*(col_blockn+1), nums[i]]=0 
                self.cands[rows_slice, col, nums[i]]=1 # Set the originals back to 1



    def Rule_1_blocks(self):
        # Applies Rule 1 to every block
    
        for block_num in np.arange(self.size):

            # The block of candidates as a 9x9 grid
            block=self.cands[self.block_nums==block_num]                
            blocksum=block.sum(axis=0) # The number of each candidate value in the block
            # Booleans of which candidate values are present 2-3 times in the block
            blocksumbool=np.logical_and(blocksum<=max(self.block_w, self.block_h), blocksum>1) 
            # The candidate values for which there are block_w or block_h or fewer candidates in that block
            nums=np.where(blocksumbool)[0]#.squeeze() 
            # A dummy index and the positions in the block of the squares with a candidate that is part of a pair or triple
            inds, pos=block[:,nums].T.nonzero() 

            # Loop over every instance of there being block_w or block_h or fewer candidates in that block
            for i in range(len(nums)): 

                # The slice of elements in pos that correspond to the squares in block that share a candidate
                pos_slice=pos[inds==i] 
                pos_slice_row=pos_slice//self.block_w # Divided by the block width to get the row number in the block
                pos_slice_col=pos_slice%self.block_w # Mod block width to get the column number in the block

                row=pos_slice_row[0] # The row number in the block of the first entry of the slice
                if(pos_slice_row==row).all(): # If the squares sharing candidates in the block are all in the same row:

                    row=row+self.block_h*(block_num//self.block_h) # The row number of the squares sharing a candidate
                    self.cands[row, :, nums[i]]=0 # Remove the candidate from all squares in the row
                        # Add back the ones in the block
                    self.cands[row,pos_slice_col+self.block_w*(block_num%self.block_h), nums[i]]=1 


                col=pos_slice_col[0] # The column number in the block of the first entry of the slice
                if(pos_slice_col==col).all(): # If the squares sharing candidates in the block are all in the same column:

                    col=col+self.block_w*(block_num%self.block_h) # The column number of the grid                
                    self.cands[:, col, nums[i]]=0 # Remove the candidate from all squares in the column
                        # Add back the ones in the block
                    self.cands[pos_slice_row+self.block_h*(block_num//self.block_h), col, nums[i]]=1 
                    
                    

                
    def Rule_1(self):
        # Applies Rule 1 to the entire grid
        
        # Apply to columns
        self.Rule_1_columns()
        
        # Apply to the rows
        self.cands=np.transpose(self.cands, [1,0,2]) # Transpose the cands array first
        self.Rule_1_columns(transpose=True) # Apply to the new 'columns'
        self.cands=np.transpose(self.cands, [1,0,2]) # Transpose it back
        
        # Apply to the blocks
        self.Rule_1_blocks()
            
    
    def Rule_2_X(self, X, group_size=2):
        # Applies Condition 2 of Rule 2 with group_size to a single set of squares from
        # a row, column, or block
        # Also functions as the logic for x-wing when fed a the grid of candidates for a single number
        
        # Proceed only if there are as many unsolved squares in the set as twice group_size
        if (X.sum(axis=1)>0).sum()>=(group_size*2):

            squares_sum=X.sum(axis=1) # The number of candidates each square in the set has
            squares_sum_cond=(squares_sum>1)&(squares_sum<=group_size) # The condition array with True values in the
                # positions where the squares have up to group_size candidates
            squares=self.inds[squares_sum_cond] # The indices of the squares which have up to group_size
                # candidates in the set

            # Proceed if the set has more than group_size squares with up to group_size candidates
            if len(squares)>=group_size:

                combs=np.array(list(it.combinations(squares, group_size))) # An array of all possible combinations
                    # of the indices of the squares with up to group_size candidates

                # Loop over every combination
                for comb in combs:

                    # Find the unique numbers for which the set of squares in comb have candidates
                    inds, nums = np.where(X[comb]==1)
                    unique_nums=np.unique(nums)

                    # Condition 2 is met if the combination of squares only has 
                    # candidates for group_size numbers between them
                    if len(unique_nums)<=group_size:

                        # Remove those numbers as candiates from all the other squares in the set
                        for pos in self.inds[np.isin(self.inds, comb, invert=True)]:

                            X[pos][unique_nums]=0
                            
        return X
            
        
    def Rule_2_group_size(self, group_size=2):
        # Applies both conditions of Rule 2 and X-wing with group_size to the whole grid
        
        for i in range(self.size):
            
            # Apply to the ith row
            self.cands[i]=self.Rule_2_X(self.cands[i], group_size)
            self.cands[i]=self.Rule_2_X(self.cands[i].T, group_size).T

            # The ith column
            self.cands[:,i]=self.Rule_2_X(self.cands[:,i], group_size)
            self.cands[:,i]=self.Rule_2_X(self.cands[:,i].T, group_size).T
            
            # The ith block
            block_cands=self.cands[self.block_nums==i]
            block_cands=self.Rule_2_X(block_cands, group_size)
            block_cands=self.Rule_2_X(block_cands.T, group_size).T
            self.cands[self.block_nums==i]=block_cands
            
            # Apply to candidates of number i for x-wing
            self.cands[:,:,i]=self.Rule_2_X(self.cands[:,:,i], group_size)
            self.cands[:,:,i]=self.Rule_2_X(self.cands[:,:,i].T, group_size).T
    
    
    def Rule_2(self):
        # Applies Rule 2 to the whole grid, considering group_size up to size//2 as necessary
        
        group_size=2
        
        # Run the loop checking with increasing group_size until a change is made
        # somewhere in cands
        self.prev_cands=self.cands.copy()
        while group_size<=self.size//2 and (self.prev_cands==self.cands).all():
            
            #print("  Group size: ", group_size)
            self.Rule_2_group_size(group_size)
            
            group_size+=1
            
    
    def Rule_3(self):
        # Applies rule 3 to the whole grid
        
        # Find the row, column, and block number of the squares with exactly 2 candidates
        cands_sum_cond=self.cands.sum(axis=2)==2 # Boolean array for which squares have two candidates
        pairs_rows, pairs_cols = np.where(cands_sum_cond) # The row and column numbers of the squares with two candidates
        pairs_blocks=self.block_nums[cands_sum_cond] # The block numbers for the squares with two candidates
        pairs_cands=self.cands[cands_sum_cond] # The candidate lists for the squares with two candidates
        pairs_cands_bool=pairs_cands==1 # Boolean candidate lists
        inds=np.arange(len(pairs_cands)) # An array to index each occurrence of two candidates in a square

        # Loop over every square with exactly two candidates
        for i in inds:

            # Find the other squares with two candidates that are in the same row, column, or block
            # and share exactly one candidate with the current square

            # Indentify the row, column, and block number of the current square
            c=pairs_cands[i] # The candidate list of the current square
            c_bool=pairs_cands_bool[i] # The boolean candidate list of the current square
            row=pairs_rows[i] # The row number of the current square
            col=pairs_cols[i] # The column number
            block_num=pairs_blocks[i] # The block number

            # Indices in the list of two-candidate squares that:
            # - share exactly one candidate with the current square
            # - intersect the current square
            shares_ints_inds=inds[((c_bool&(c==pairs_cands)).sum(axis=1)==1)&\
                                  ((pairs_rows==row)|(pairs_cols==col)|(pairs_blocks==block_num))]

            
            # Check to see if two of them also share a candidate but don't intersect with the
            # current square in the same way

            # The combinations of pairs of squares meeting the above criteria
            combs=np.array(list(it.combinations(shares_ints_inds, 2)))

            # Check every pair combination
            for comb in combs:

                i1=comb[0]
                i2=comb[1]

                # Boolean for whether the two squares intersect each other
                intersect_eachother=pairs_rows[i1]==pairs_rows[i2] or\
                                    pairs_cols[i1]==pairs_cols[i2] or\
                                    pairs_blocks[i1]==pairs_blocks[i2]

                # Check whether the two squares share a candidate that is not in the original square

                # Boolean list for the numbers for which the two sqaures in comb share a candidate
                shared_cands_bool=pairs_cands_bool[i1]&(pairs_cands[i1]==pairs_cands[i2])

                # If the two squares:
                # - do not intersect
                # - share exactly one candidate
                # - do not share a candidate that is also in the current square
                # we have y-wing
                if not intersect_eachother and shared_cands_bool.sum()==1 and not (shared_cands_bool&c_bool).any():

                    # Eliminate the candidate from squares intersecting both secondary squares

                    num=self.inds[shared_cands_bool] # The number to be eliminated as a candidate
                    
                    # Eliminate the number as a candidate based on row and column intersections
                    self.cands[pairs_rows[i1], pairs_cols[i2], num]=0
                    self.cands[pairs_rows[i2], pairs_cols[i1], num]=0

                    # Eliminate the number as a candidate based on block intersections
                    # Boolean array indicating the squares that are in the same block as one of the two y-wing squares
                    # and in the same row or column as the other
                    block_intersect_bool=((self.block_nums==pairs_blocks[i1])&\
                                            ((self.row_nums==pairs_rows[i2])|(self.col_nums==pairs_cols[i2])))|\
                                         ((self.block_nums==pairs_blocks[i2])&\
                                            ((self.row_nums==pairs_rows[i1])|(self.col_nums==pairs_cols[i1])))

                    # The list of rows and columns where block_intersect_bool is True
                    rs, cs = np.where(block_intersect_bool)
                    self.cands[rs, cs, num]=0 # Eliminate the number as a candidate in those squares
    
    
    def Rule_4(self):
        # Applies Rule 4 
            
        # The first time we have to start guessing, permanently record the current state of 
        # cands and grid and establish the list of squares to use for geussing
        if self.rule_4_count==0:
            self.current_cands=self.cands.copy()
            self.current_grid=self.grid.copy()

            # Find the row and column numbers of the squares with exactly 2 candidates
            cands_sum_cond=self.cands.sum(axis=2)==2 # Boolean array for which squares have two candidates
            # The row and column numbers of the squares with two candidates
            self.pairs_rows, self.pairs_cols = np.where(cands_sum_cond) 
            
        # If we have checked both candidates in every two-candidate square
        # we couldn't solve the puzzle, so break out of the solve loop
        # by not changing any candidates
        if self.rule_4_count>=2*len(self.pairs_rows):
            return None

        # Reset cands and grid to the state they were in before
        # we started guessing
        self.cands=self.current_cands.copy()
        self.grid=self.current_grid.copy()

        # If Rule 4 has been called an even number of times, it is time to move on
        # to the next square with two candidates
        if self.rule_4_count%2==0:

            guess_ind=self.rule_4_count//2

            # Establish the coordinates of the guess we are making
            self.guess_row=self.pairs_rows[guess_ind]
            self.guess_col=self.pairs_cols[guess_ind]
            self.guess_nums=self.inds[self.cands[self.guess_row, self.guess_col]==1]
            guess_num=self.guess_nums[0]


        # If Rule 4 has been called an odd number of times, it is time
        # to check the second candidate of the current square
        else:
            guess_num=self.guess_nums[1]


        # Eliminate the chosen candidate
        self.cands[self.guess_row, self.guess_col, guess_num]=0

        # Update the number of time Rule 4 has been called
        self.rule_4_count+=1
        

    
    def is_solved(self):
        # Checks if the grid is solved and updates and returns the solved state as a boolean value
        
        # Do a quick check by checking if there are any blank spots still in the grid
        self.solved=(self.grid!=0).all()
        
        # If no blank spots remain, do a more thorough check to make sure there is 
        # exactly one of every number in each row, column, and block
        if self.solved:
            for i in range(self.size):

                nums, counts_blocks = np.unique(self.grid[self.block_nums==i], return_counts=True)
                nums, counts_rows=np.unique(self.grid[i], return_counts=True)
                nums, counts_cols=np.unique(self.grid[:,i], return_counts=True)

                self.solved=self.solved and (counts_rows==1).all() and (counts_cols==1).all() and (counts_blocks==1).all()
        
        return self.solved
    
    
    def solve_step(self):
        # Based on the current list of candidates, try to fill in any squares with only one
        # candidate or where a square has the only candidate for that value in its
        # row, column, or block

        # Fill in spots with only once candidate
        locs=np.sum(self.cands, axis=2)==1
        self.grid[locs]=np.where(self.cands[locs]==1)[1]+1

        # Fill in spots where a candidate is the only one of its value in its row, column, or block
        # Sum all the candidate vectors in a given row, and any position with a value of 1 indicates
        # the value for which there is only one square with that potential candidate

        # Columns
        cols, nums = np.where(np.sum(self.cands, axis=0)==1)
        inds, rows = self.cands[:, cols, nums].T.nonzero()
        self.grid[rows, cols]=nums+1

        # Rows
        rows, nums = np.where(np.sum(self.cands, axis=1)==1)
        inds, cols = self.cands[rows, :, nums].nonzero()
        self.grid[rows, cols]=nums+1

        # Blocks
        for block_num in np.arange(self.size):

            block=self.cands[self.block_nums==block_num]
                
            nums=np.where(block.sum(axis=0)==1)[0].squeeze()
            inds=block[:,nums].T.nonzero()[-1].squeeze()
                        
            self.grid[self.block_nums==block_num][inds]=nums+1

                
                
    def solve_loop(self):
        # Iterates the solving procedure until the puzzle is solved or deemed unsolvable
            
        self.prev_cands=self.cands.copy() # Update the previous state of cands

        # Try eliminating candidates using all the rules until a change is made to cands
        # or it runs out of rules
        rule=0
        while (self.cands==self.prev_cands).all() and rule<len(self.rule_func_list):

            # Apply the current rule
            # print("Rule %d"%rule)
            self.rule_func_list[rule]()
            self.max_rule=max(rule, self.max_rule)
            rule+=1

        # If a change was made by the Rules
        if (self.prev_cands!=self.cands).any():

            self.solve_step() # Fill in values according to the current state of cands
            self.num_steps+=1

            # If that solved the puzzle
            if self.is_solved():
                #print("Solved in %d steps."%self.num_steps)
                #print("The highest rule used was Rule %d."%self.max_rule)
                None
                
            # If not
            else:
                # Start back at the top of the function
                self.solve_loop()
        
        # If no change was made by the Rules, then it is not solved
        # and there is nothing more to do
        else:
            # Revert cands and grid to the state before the program started guessing
            self.cands=self.current_cands
            self.grid=self.current_grid
            #print("I couldn't solve it.")
            
            
def main():

    grid=np.array([[1,7,0,0,0,2,0,9,5],
                   [4,0,0,0,0,0,0,0,0],
                   [0,0,0,0,8,0,0,2,0],
                   [2,5,0,0,0,8,0,0,1],
                   [0,0,0,3,0,0,6,0,0],
                   [0,0,9,0,0,0,0,0,0],
                   [7,9,0,0,6,0,1,0,0],
                   [0,0,8,0,0,0,0,0,9],
                   [0,0,4,0,0,7,0,0,0]])
    
    puzzle=Sudoku_Puzzle(grid)
    print("The puzzle: ")
    print(puzzle.grid)
    puzzle.solve_loop()
    print(puzzle.grid)
    
    
if __name__=="__main__":

    main()
    
    