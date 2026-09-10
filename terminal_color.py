class TerminalColor:
    """
    Manage terminal colors using ANSI escape codes.
    """

    COLORS = {
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "orange": "\033[38;5;208m",
        "purple": "\033[38;5;129m",
        "brown": "\033[38;5;130m",
        "lime": "\033[38;5;154m",
        "gold": "\033[38;5;220m",
        "maroon": "\033[38;5;88m",
        "darkred": "\033[38;5;52m",
        "violet": "\033[38;5;177m",
        "crimson": "\033[38;5;197m",
    }

    RESET = "\033[0m"

    def colorize(self, text: str, color: str) -> str:
        """
        Apply a terminal color to a text.
        """
        if color == "rainbow":
            return self.rainbow(text)

        code = self.COLORS.get(color)
        if code is None:
            return text

        return f"{code}{text}{self.RESET}"

    def rainbow(self, text: str) -> str:
        """
        Print text using several terminal colors.
        """
        colors = [
            "\033[31m",  # red
            "\033[33m",  # yellow
            "\033[32m",  # green
            "\033[36m",  # cyan
            "\033[34m",  # blue
            "\033[35m",  # magenta
        ]

        result = ""
        for index, character in enumerate(text):
            color = colors[index % len(colors)]
            result += f"{color}{character}"

        return f"{result}{self.RESET}"
