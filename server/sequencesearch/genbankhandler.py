from Bio import Entrez
from Bio import SeqIO

import os
from datetime import datetime
from math import ceil
from concurrent.futures import Future, ThreadPoolExecutor

from config.settings import get_env_value

class GenBankHandler:
    # In real life, these constants would be tweaked to optimize performance.
    # When I tried playing with them, they didn't seem to affect performance much.
    # Maybe it would be more useful on a large file? Or maybe that's not where the bottleneck is.
    MAX_THREADS = get_env_value('GB_APP_MAX_THREADS', 5)
    MAX_CHUNK_SIZE = get_env_value('GB_APP_MAX_CHUNK_SIZE', 100000)

    organisms_to_search = ("NC_000852", "NC_007346", "NC_008724", "NC_009899", "NC_014637",
        "NC_020104", "NC_023423", "NC_023640", "NC_023719", "NC_027867")
    genbank_file_paths = []

    # In a more involved system with many files, might make sense to store these in S3,
    # since there's more space available there than on the local machine, but the files
    # would still be reasonably quick to download.
    # It would depend a lot on the number of files, their size, and amount of disk space 
    # on the machines are running the app.
    def write_files(self):
        for organism in self.organisms_to_search:
            filepath = f'{os.path.dirname(os.path.abspath(__file__))}/../genbank_files/{organism}.gbk'
            self.genbank_file_paths.append(filepath)
            if (not os.path.exists(filepath)):
                Entrez.email = "magidson.sarah@gmail.com"
                with Entrez.efetch(
                    db="nucleotide", rettype="gb", retmode="text", id=organism
                ) as handle:
                    with open(filepath, 'w+') as file:
                        print(f'{datetime.now()} Writing file for {organism}...')
                        content = handle.read()
                        file.write(content)
                        print(f'{datetime.now()} Done')

    def get_protein_at_position(self, seq_record, start_position, seq_len):
        protein_name = "Unknown"

        # features seem to be ordered by start position, which makes finding the right range easier
        for feature in seq_record.features:
            # CDS features seem the ones that provide protein ids
            if feature.type != 'CDS':
                continue

            # a more precise version of this logic would use the ExactPosition.extension
            # to determine the _exact_ locations to look at
            if feature.location.nofuzzy_end >= start_position + seq_len:
                if feature.location.nofuzzy_start <= start_position:
                    protein_name = feature.qualifiers['protein_id'][0]
                    break
                else:
                    # In this case, the sequence did not fall neatly in range of known protein
                    break
        
        return protein_name

    def search_for_sequence(self, sequence):
        self.write_files()
        query = sequence.upper()

        # Break up files into pools for threads to search faster
        filelists = tuple([] for _ in range(self.MAX_THREADS))
        for i in range(len(self.genbank_file_paths)):
            filelists[i % len(filelists)].append(self.genbank_file_paths[i])

        threads = []
        with ThreadPoolExecutor(max_workers=self.MAX_THREADS) as executor:
            for filelist in filelists:
                threads.append(executor.submit(self.search_for_sequence_in_files, query, filelist))

            result = None

            for thread in threads:
                if (result is not None):
                    # Only need one good result -- ignore the rest
                    thread.cancel()
                    continue
                thread_result = thread.result()
                if thread_result is not None:
                    result = thread_result

        if result is not None:
            seq_record = result.pop('seq_record')
            result['protein_name'] = self.get_protein_at_position(seq_record, result['position'], len(query))
        else:
            result = { 'organism': None, 'position': None, 'protein_name': None }
            
        return result

    
    def search_for_sequence_in_files(self, query, filelist):
        result = None
        for file in filelist:
            seq_records = SeqIO.parse(file, "gb")  # using "gb" as an alias for "genbank"
            for seq_record in seq_records:
                seq = str(seq_record.seq)

                # open question - does it count if the desired sequence crosses the boundary between two proteins?
                # does that count as finding it? Or is that not valid?
                # Not going to worry about that here.
                start_position = self.chunked_search(query, seq)

                if (start_position >= 0):
                    result = {
                        'organism': seq_record.annotations['organism'],
                        'organism_id': seq_record.id,
                        'position': start_position,
                        'seq_record': seq_record
                    }
                    break
            
        return result

    # improve search time by using multiple threads to search file content
    def chunked_search(self, query, full_seq):
        # print(f'{datetime.now()} Starting search')
        results = []
        threads = []

        full_seq_len = len(full_seq)
        chunk_size = min(self.MAX_CHUNK_SIZE, ceil(full_seq_len / self.MAX_THREADS))

        start = 0

        with ThreadPoolExecutor(max_workers=self.MAX_THREADS) as executor:
            while start < full_seq_len:
                threads.append(executor.submit(self.search_seq_chunk, query, full_seq, start, chunk_size))
                start = start + chunk_size
            
            for thread in threads:
                results.append(thread.result())

        # print(f'{datetime.now()} Search complete')
        for result in results:
            if result >= 0:
                return result + 1

        return -1

    def search_seq_chunk(self, query, full_seq, start, chunk_size):
        end_position = start + chunk_size + len(query) - 1
        found = full_seq.find(query, start, end_position)
        # print(f'found: {found}, start: {start}, end: {end_position}, opening seq: {full_seq[start:start+10]}')
        return found
