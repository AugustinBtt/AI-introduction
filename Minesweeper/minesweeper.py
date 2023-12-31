import itertools
import random


class Minesweeper(): #handles gameplay
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.width):
            row = []
            for j in range(self.height):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(width)
            j = random.randrange(height)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.width):
            print("--" * self.height + "-")
            for j in range(self.height):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.height + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.width and 0 <= j < self.height:
                    if self.board[i][j]: #if the cell contains True which means there is a mine
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def __hash__(self):
        return hash((frozenset(self.cells), self.count))


    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        return set()


    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1


    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI(): #handles inferring which moves to make based on knowledge
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        print(f"Function called by cell: {cell}")
        print(f"Number of mines around cell {cell}: {count}")

        if not (0 <= cell[0] < self.height and 0 <= cell[1] < self.width):
            return

        self.moves_made.add(cell)
        self.safes.add(cell)

        # Get neighboring cells
        neighbors = {(cell[0] + i, cell[1] + j) for i in (-1, 0, 1) for j in (-1, 0, 1)
                     if 0 <= cell[0] + i < self.width and 0 <= cell[1] + j < self.height}

        neighbors.discard(cell)

        undetermined_cells = [x for x in neighbors if x not in self.mines and x not in self.safes]
        if undetermined_cells:
            new_sentence = Sentence(cells=undetermined_cells, count=count)
            self.knowledge.append(new_sentence)

        previous_safes = set()
        previous_mines = set()
        previous_knowledge_length = 0


        while True:
            #Basic Deductions
            for sentence in self.knowledge:
                if sentence.count == 0:
                    safes = set(sentence.cells)
                    sentence.cells.clear()
                    for safe in safes:
                        self.mark_safe(safe)

                elif len(sentence.cells) == sentence.count:
                    mines = set(sentence.cells)
                    sentence.cells.clear()
                    for mine in mines:
                        self.mark_mine(mine)

            print(f"Inferred safes: {self.safes - self.moves_made}")
            print(f"Inferred mines: {self.mines}")

            if (self.safes == previous_safes and self.mines == previous_mines and len(self.knowledge) == previous_knowledge_length):
                break

                # Update the previous states:
            previous_safes = self.safes.copy()
            previous_mines = self.mines.copy()
            previous_knowledge_length = len(self.knowledge)


            #Advanced deductions
            new_knowledge = set()
            knowledge_reprs = {(frozenset(sentence.cells), sentence.count) for sentence in self.knowledge}

            for sentenceA in self.knowledge:
                for sentenceB in self.knowledge:
                    if sentenceA != sentenceB and sentenceA.cells.issubset(sentenceB.cells):
                        new_cells = sentenceB.cells - sentenceA.cells
                        new_count = sentenceB.count - sentenceA.count
                        new_sentence = Sentence(new_cells, new_count)

                        # hashable representation of the new_sentence
                        new_sentence_repr = (frozenset(new_sentence.cells), new_sentence.count)

                        # check if this representation is not already in knowledge
                        if new_sentence_repr not in knowledge_reprs:
                            knowledge_reprs.add(new_sentence_repr)
                            new_knowledge.add(new_sentence)
                            print(f"New knowledge from advanced deduction: {knowledge_reprs}")

            # add the new knowledge (Sentences) to the self.knowledge list
            self.knowledge.extend(new_knowledge)

            # clean up the knowledge base by removing empty sentences
            self.knowledge = [s for s in self.knowledge if s.cells and s.count != 0]

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for move in self.safes:
            if move not in self.moves_made:
                return move
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # all possible moves on the board
        all_possible_moves = [(i, j) for i in range(self.width) for j in range(self.height)]

        available_moves = [move for move in all_possible_moves if move not in self.moves_made and move not in self.mines]

        if not available_moves:
            return None

        return random.choice(available_moves)