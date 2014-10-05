from blockwar import BlockWar
from util.log import LoggingConfigurator

# Configure logging
LoggingConfigurator()

# Run Block War
block_war = BlockWar()

try:
    block_war.run()
except KeyboardInterrupt:
    block_war.quit()
