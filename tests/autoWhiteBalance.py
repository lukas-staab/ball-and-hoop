import repackage
repackage.up()
from src.ballandhoop.whiteBalancing import WhiteBalancing

wb = WhiteBalancing()
print(wb.calculate())