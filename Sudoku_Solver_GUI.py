import tkinter as tk
import numpy as np
from Sudoku_Solver import Sudoku_Puzzle

class SudokuGUI:
    def __init__(self, master):
    # Initialize variables, lists, frames, and buttons
        self.master = master
        self.master.title("Sudoku Solver")
        
        # The default size and block dimensions of the Sudoku puzzle
        self.size=9
        self.blockw=3
        self.blockh=3
        
        # Boolean for whether the entries in the grid are acceptable
        self.grid_ok=True
              
        # Use a list to go from numbers used in the solving process to displaying
        # numbers and letters as necessary
        self.num_map_list=['1', '2', '3', '4', '5', '6', '7', '8', '9', 
              'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
              'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
              'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X',
              'Y', 'Z', 'AA']
        
        # Create a dictionary to map numbers and letters provided by the user
        # to the numbers used in the solving process
        self.num_map={}
        for i, item in enumerate(self.num_map_list):
            self.num_map[item]=i+1
        
        self.create_entry_frame()
        
        # Make a frame for the buttons underneath
        self.button_frame=tk.Frame(self.master, borderwidth=2, relief=tk.FLAT)
        self.button_frame.grid(column=0, row=1, padx=10, pady=0)

        # Create a Solve button
        solve_button = tk.Button(self.button_frame, text="Solve", command=self.solve)
        solve_button.pack(side=tk.LEFT, padx=10, pady=10)
        # Allow the Enter key to command the solve as well
        self.master.bind("<Return>", self.solve_event)
        
        # Create a clear button
        clear_button = tk.Button(self.button_frame, text="Clear", command=self.clear)
        clear_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Create a reset button
        reset_button = tk.Button(self.button_frame, text="Reset", command=self.reset)
        reset_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Create entry fields for a custom size and block width
        custom_size_label=tk.Label(self.button_frame, text="Custom size")
        custom_size_label.pack(side=tk.LEFT, padx=2, pady=10)
        self.custom_size_entry=tk.Entry(self.button_frame, font=('Arial', 10), width=2)
        self.custom_size_entry.pack(side=tk.LEFT, padx=10, pady=10)
        
        custom_blockw_label=tk.Label(self.button_frame, text="Block width")
        custom_blockw_label.pack(side=tk.LEFT, padx=2, pady=10)
        self.custom_blockw_entry=tk.Entry(self.button_frame, font=('Arial', 10), width=2)
        self.custom_blockw_entry.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Custom size button
        custom_button=tk.Button(self.button_frame, text="Change size", command=self.change_size)
        custom_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Create a box to display messages
        self.text_frame=tk.Frame(self.master, borderwidth=2, relief=tk.FLAT)
        self.text_frame.grid(column=0, row=2, padx=10, pady=0)
        self.text=tk.Label(self.text_frame, 
        text="Input the numbers of the Sudoku puzzle or select a different puzzle size.")
        self.text.pack(side=tk.TOP, padx=10, pady=0)
                            
    
    def create_entry_frame(self):     
        # Create a grid of Entry widgets inside a Frame with a border
        self.entry_frame = tk.Frame(self.master, borderwidth=2,
                                 relief=tk.FLAT, name="entryframe",
                                 bg='white')
        self.entry_frame.grid(column=0, row=0, pady=10)
        self.entries = []
        for i in range(self.size):
            row = []
            for j in range(self.size):
                entry = tk.Entry(self.entry_frame,
                                 name=str(i)+","+str(j),
                                 width=2,
                                 font=('Arial', 16),
                                 highlightthickness=1,
                                 highlightcolor='#00bbff',
                                 insertontime=0,
                                 relief=tk.FLAT)
                entry.grid(row=i, column=j, padx=2, pady=2)
                row.append(entry)
            self.entries.append(row)
            
        self.entries[0][0].focus()
            
        # Bind arrow keys to functions that traverse the focus
        self.master.bind_class("Entry", '<Down>', self.downKey)
        self.master.bind_class("Entry", '<Up>', self.upKey)
        self.master.bind_class("Entry", '<Left>', self.leftKey)
        self.master.bind_class("Entry", '<Right>', self.rightKey)

    # Functions the allow the user to use arrow keys to move the focus around
    # the grid        
    def downKey(self, event):
        i, j = str(self.master.focus_get())[12:].split(',')
        self.entries[(int(i)+1)%self.size][int(j)].focus()
        
    def upKey(self, event):
        i, j = str(self.master.focus_get())[12:].split(',')
        self.entries[(int(i)-1)%self.size][int(j)].focus()
    
    def leftKey(self, event):
        i, j = str(self.master.focus_get())[12:].split(',')
        self.entries[int(i)][(int(j)-1)%self.size].focus()
    
    def rightKey(self, event):
        i, j = str(self.master.focus_get())[12:].split(',')
        self.entries[int(i)][(int(j)+1)%self.size].focus()  
        
        
    def clear(self):
        # Delete the contents of every entry
        for i in range(self.size):
            for j in range(self.size):
                self.entries[i][j].delete(0, tk.END)
                
        self.text.config(\
        text="Input the numbers of the Sudoku puzzle or select a different puzzle size.")
                
                
    def reset(self):
        # Reset the entry grid to what the user inputted.
        for i in range(self.size):
            for j in range(self.size):
                value=self.grid[i][j]
                self.entries[i][j].delete(0, tk.END)
                
                if value:
                    self.entries[i][j].insert(0, self.num_map_list[value-1])
        
        
    def solve(self):
    # Take the values provided by the user in the entry grid and feed them to
    # the solving algorithm. Then display the solution in the entry grid.
    
    # Create a 2D array with the entry values, checking if they are appropriate
    # and filling in the array with 0 where there is no entry.
        valid_entries=True
        self.grid = np.zeros((self.size, self.size))
        for i, row in enumerate(self.entries):
            for j, entry in enumerate(row):
                value = entry.get().upper() # To allow upper and lower case letters
                
                # Check if the value in the entry is in the number map
                # and less than the size of the puzzle
                if value in self.num_map: 
                    value_num=self.num_map[value]
                    self.grid[i, j]=self.num_map[value]
                        
                elif value:
                    self.text.config(text="One or more invalid entries.")
                    entry.delete(0, tk.END)
                    valid_entries=False

        self.grid=self.grid.astype('int')        
        
        # Check the grid for errors
        if self.check_grid_ok() and valid_entries:
        
            # Solve the puzzle
            puzzle=Sudoku_Puzzle(self.grid, self.blockw)    
            puzzle.solve_loop()              
            solution = puzzle.grid
            
            if puzzle.is_solved():
                self.text.config(text="Solved in %d steps.\nThe highest rule used was Rule %d."\
                %(puzzle.num_steps, puzzle.max_rule))
            else:
                self.text.config(text="I was not able to solve the puzzle.")
    
            # Fill in the solution in the Entry widgets
            for i in range(self.size):
                for j in range(self.size):
                    self.entries[i][j].delete(0, tk.END)
                    x=solution[i][j]
                    if x!=0:
                        self.entries[i][j].insert(0, self.num_map_list[x-1])
                
                
    def solve_event(self, event):
    # Calls the solve function as an event
        self.solve()
        
    
    def check_grid_ok(self):
    # Checks the input grid and raises value errors if it is not square or if 
    # any of the rows, columns, or blocks contain more than one of any number
    
        self.grid_ok=True
    
    # Inform the user if the grid contains numbers of a higher value than its size
    # and don't allow the solving to proceed.
        if (self.grid>self.size).any():
        
            self.grid_ok=False
            self.text.config(text='Inputs contain numbers greater than the puzzle size.')
            
            
        # If the grid is empty, request entries
        if (self.grid==0).all():
            self.grid_ok=False
            #self.text.config(text="Please enter numbers in the grid.")
        
            
        nums_okay=True # A boolean value for whether there is more than one of 
        # each number in any row, column, or block
        
        # Check if there is more than one of each number in any row, column, or block
        # If such a conflict is found, end the loop
        i=0
        while i<self.size and nums_okay:
        
            # Count the number of each number in each row, column, and block
            nums_blocks, counts_blocks = np.unique(\
            self.grid[self.blockh*(i//self.blockh):self.blockh*(i//self.blockh+1),\
                            self.blockw*(i%self.blockh):self.blockw*(i%self.blockh+1)],\
             return_counts=True)
            nums_rows, counts_rows=np.unique(self.grid[i], return_counts=True)
            nums_cols, counts_cols=np.unique(self.grid[:,i], return_counts=True)
        
            # If the current rows, columns, and blocks each have fewer than two of every number,
            # (except for 0) then the input grid continues to be acceptable
            nums_okay=nums_okay and\
                      (counts_rows[nums_rows!=0]<2).all() and\
                      (counts_cols[nums_cols!=0]<2).all() and\
                      (counts_blocks[nums_blocks!=0]<2).all()
            i+=1
            
        # If more than one of a number is found in any set, inform the user
        # and don't proceed with the solving.
        if not nums_okay:
            self.grid_ok=False
            self.text.config(text="Input numbers conflict.")
            
        return self.grid_ok
    
    
    def change_size(self):
    # Based on input from the user, change the size of the Sudoku puzzle
        
        change_size_ok=True
        try:                      
            self.size=int(self.custom_size_entry.get())
            self.blockw=int(self.custom_blockw_entry.get())
            
        except ValueError:
            change_size_ok=False
            self.text.config(text="Custom size or block width not interpretable as an integer.")
        
        
        if change_size_ok:
            # Change the size only if the given size and block width are acceptable
            if self.blockw>0 and self.size>0 and self.blockw<=self.size and\
                    self.size%self.blockw==0 and self.size!=self.blockw and\
                    self.size<=len(self.num_map):
                
                self.blockh=self.size//self.blockw
                self.entry_frame.destroy()
                self.create_entry_frame()
                
            else:
                self.text.config(text="Custom size or block width not acceptable.")
                  

            

# Create the main window and run the GUI
root = tk.Tk()
root.geometry("600x600")
sudoku_gui = SudokuGUI(root)
root.mainloop()
