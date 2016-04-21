from tuneful.database import session
from tuneful.models import Song, File
fileA=File(name="Shady_Grove.mp3")
songA=Song(filename=fileA)


session.add_all(songA, fileA)
session.commit()

print(songA)