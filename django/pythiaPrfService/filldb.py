"""
Fill the database with realistic entries for space measurements.
"""
import datastore
from settings import dp

# Fill the database state table with random w entries.
def fillStateTable(start=31860, n=68140):
    for i in range(n):
        # Print periodic updates
        if i and i % 1000 == 0:
            dp(i=i+start)
        datastore.getStateEntry(start+i)


# Run!
if __name__ == "__main__":
    fillStateTable()
