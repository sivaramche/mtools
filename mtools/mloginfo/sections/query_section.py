from base_section import BaseSection

from mtools.util.profile_collection import ProfileCollection
from mtools.util.grouping import Grouping
from mtools.util.print_table import print_table
from mtools.util import OrderedDict

import numpy as np

class QuerySection(BaseSection):
    """ 
    """
    
    name = "queries"

    def __init__(self, mloginfo):
        BaseSection.__init__(self, mloginfo)

        # add --queries flag to argparser
        self.mloginfo.argparser_sectiongroup.add_argument('--queries', action='store_true', help='outputs statistics about query patterns')

        # progress bar
        self.progress_bar_enabled = not self.mloginfo.is_stdin


    @property
    def active(self):
        """ return boolean if this section is active. """
        return self.mloginfo.args['queries']


    def run(self):
        """ run this section and print out information. """
        grouping = Grouping(group_by='pattern')
        logfile = self.mloginfo.logfile

        if logfile.start and logfile.end and not self.mloginfo.args['verbose']:
            progress_start = self.mloginfo._datetime_to_epoch(logfile.start)
            progress_total = self.mloginfo._datetime_to_epoch(logfile.end) - progress_start
        else:
            self.progress_bar_enabled = False


        for i, le in enumerate(logfile):

            # update progress bar every 1000 lines
            if self.progress_bar_enabled and (i % 1000 == 0):
                if le.datetime:
                    progress_curr = self.mloginfo._datetime_to_epoch(le.datetime)
                    self.mloginfo.update_progress(float(progress_curr-progress_start) / progress_total)

            if le.operation in ['query', 'update', 'remove']:
                # print le.pattern
                grouping.add(le)

        grouping.sort_by_size()

        # clear progress bar again
        self.mloginfo.update_progress(1.0)

        table_rows = []
        for g in grouping:
            # calculate statistics for this group

            stats = OrderedDict()
            stats['pattern'] = g
            stats['count'] = len( [le for le in grouping[g] if le.duration] )
            stats['min'] = min( le.duration for le in grouping[g] if le.duration )
            stats['max'] = max( le.duration for le in grouping[g] if le.duration )
            stats['mean'] = 0
            stats['sum'] = sum( le.duration for le in grouping[g] if le.duration )
            stats['mean'] = stats['sum'] / stats['count']

            table_rows.append(stats)

        print_table(table_rows, ['pattern', 'count', 'min (ms)', 'max (ms)', 'mean (ms)', 'sum (ms)'], uppercase_headers=False)
        print 

