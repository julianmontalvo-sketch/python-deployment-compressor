"""
Module docstring.
"""

import math

# This comment should disappear


class Calculator:
    """
    Class docstring.
    """

    def area(self, radius):
        """
        Function docstring.
        """

        text = "# this is NOT a comment"

        multiline = """
Hello
World
"""

        print(text)

        return math.pi * radius * radius + len(multiline)


if __name__ == "__main__":
    calculator = Calculator()

    print(calculator.area(10))
