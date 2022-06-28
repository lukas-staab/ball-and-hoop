import repackage
repackage.up()
from src.ballandhoop.whiteBalancing import WhiteBalancing

print(WhiteBalancing(verboseOutput=True).calculate())