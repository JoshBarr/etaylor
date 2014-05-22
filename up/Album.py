class Album(object):
    """
    A generic container for all the album stuff
    """
    question = 1
    title = "Up: Side A"
    artist = "E Taylor"
    genre = "Rap"
    year = "2014"
    composer = "Elliot Taylor"
    tracks = [
        {
            "filename": "1-e-taylor-little-empire.mp3",
            "title": "Little Empire"
        },
        {
            "filename": "2-e-taylor-back-you-up.mp3",
            "title": "Back You Up Feat. Bella Kalolo"
        },
        {
            "filename": "3-e-taylor-ego.mp3",
            "title": "Ego"
        },
        {
            "filename": "4-e-taylor-new-york-any-nickel.mp3",
            "title": "New York (Any Nickel)"

        },
        {
            "filename": "5-e-taylor-central-park.mp3",
            "title": "Central Park"
        }
    ]

    def get_tracks(self):
        return self.tracks