def update_elo_rating(winner_rating, loser_rating, k=32):
    expected_winner = 1 / (1 + 10 ** ((loser_rating - winner_rating) / 400))
    expected_loser = 1 - expected_winner

    winner_new_rating = winner_rating + k * (1 - expected_winner)
    loser_new_rating = loser_rating + k * (0 - expected_loser)

    return winner_new_rating, loser_new_rating
