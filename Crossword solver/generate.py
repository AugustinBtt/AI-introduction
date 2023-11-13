import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # make sure that every value in a variable’s domain has the same number of letters as the variable’s length
        for variable in self.crossword.variables:
            possible_words = self.domains[variable].copy()
            for word in possible_words:
                if len(word) != variable.length:
                    self.domains[variable].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        overlap = self.crossword.overlaps[x, y]

        if overlap is None:
            return False

        x_index, y_index = overlap

        for x_value in set(self.domains[x]):
            if not any(x_value[x_index] == y_value[y_index] for y_value in self.domains[y]):
                self.domains[x].remove(x_value)
                revised = True

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            queue = [(X, Y) for X in self.crossword.variables for Y in self.crossword.neighbors(X)]
        else:
            queue = arcs

        while queue:
            x, y = queue.pop(0)
            if self.revise(x, y):
                if not self.domains[x]:
                    return False

                for z in self.crossword.neighbors(x) - {y}:
                    queue.append((z, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        all_variables = set(self.crossword.variables)

        assigned_variables = set(assignment.keys())

        return all_variables == assigned_variables

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        words = list(assignment.values())
        if len(words) != len(set(words)):
            return False

        for variable, value in assignment.items():
            if len(value) != variable.length:
                return False

            for neighbor in self.crossword.neighbors(variable):
                if neighbor in assignment:
                    overlap = self.crossword.overlaps[variable, neighbor]
                    # retrieve the specific overlapping position between the current variable and its neighbor
                    if overlap is not None:
                        v_index, n_index = overlap  # unpack tuple
                        if value[v_index] != assignment[neighbor][n_index]:
                            return False
        return True

    def count_ruled_out_values(self, value, var, assignment):
        count = 0
        for neighbor in self.crossword.neighbors(var):
            if neighbor in assignment:
                overlap = self.crossword.overlaps[var, neighbor]  # finds where overlap between var and neighbor
                if value[overlap[0]] != assignment[neighbor][overlap[1]]:
                    count += 1
        return count

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        values_with_counts = [(value, self.count_ruled_out_values(value, var, assignment)) for value in
                              self.domains[var]]
        # each tuple contains a word from the domain of var and the associated count of how many options it rules out

        values_with_counts.sort(key=lambda x: x[1])

        return [value for value, _ in values_with_counts]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_var = {}
        for var in self.crossword.variables:
            if var not in assignment:
                viable_words_count = 0

                for word in self.domains[var]:
                    if self.is_word_viable(word, var, assignment):
                        viable_words_count += 1

                unassigned_var[var] = viable_words_count

        sorted_var = dict(sorted(unassigned_var.items(), key=lambda item: item[1]))
        min_value = min(sorted_var.values())

        var_low_domain = [key for key, value in sorted_var.items() if value == min_value]

        if len(var_low_domain) > 1:  # if there is a tie
            max_degree = 0
            var_max_degree = None
            for var in var_low_domain:
                nb_intersections = len(self.crossword.neighbors(var))
                if nb_intersections > max_degree:
                    max_degree = nb_intersections
                    var_max_degree = var
            return var_max_degree if var_max_degree is not None else var_low_domain[0]
        else:
            return var_low_domain[0]

    def is_word_viable(self, word, var, assignment):
        for neighbor in self.crossword.neighbors(var):
            if neighbor in assignment:
                i, j = self.crossword.overlaps[var, neighbor]
                if word[i] != assignment[neighbor][j]:
                # check that the letter in the candidate word at position i matches the letter in the already placed word (in the intersecting space) at position j
                    return False
        return True

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            del assignment[var]

        return None


def main():
    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()