from blockwar import BlockWar, QuitEvent
from util import log, paths

# Configure logging
log.configure(file_path=paths.env(), file_name='log.txt')

# Run Block War
block_war = BlockWar()
block_war.initialize()

try:
    block_war.run()
except(KeyboardInterrupt, QuitEvent), ex:
    block_war.quit()
