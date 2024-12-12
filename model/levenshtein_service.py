class LevenshteinService():
    """
    Service for calculating the Levenshtein distance between 2 strings
    """
    def distance(self, str1, str2):
        """Calculate the Levenshtein distance between 2 strings

        Args:
            str1 (str): the first string
            str2 (str): the second string

        Returns:
            integer: the distance between 2 strings
        """
        m, n = len(str1), len(str2)
        dp = [[0 for _ in range(n + 1)] for _ in range(m + 1)]

        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if str1[i - 1] == str2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

        return dp[m][n]

    def single_similarity(self, str1: str, str2: str) -> float:
        """Calculate the similarity of 2 input string

        Args:
            str1 (string): the main input
            str2 (string): the other input

        Returns:
            float: percentage of similarity
        """
        distance = self.distance(str1, str2)
        return distance/len(str1)

    def bulk_similarity(self, s: str, list_str: list[str]) -> list[float]:
        """Calculate the similarity between one string and a list of other strings

        Args:
            s (str): the input string
            list_str (list[str]): list of other strings

        Returns:
            list[float]: list of scores
        """
        scores = []
        for sub_s in list_str:
            scores.append(self.single_similarity(s, sub_s))
        return scores