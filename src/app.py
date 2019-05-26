import index
import eva
import sent
import sys
import configure

if __name__ == "__main__":
    # run_mode = sys.argv[1]
    run_mode = configure.DEV_MODE

    # index.sort_by_wiki()
    # index.sort_by_corpus()
    # index.dump_topics()
    # index.dump_capitals()
    # print("indexing done")
    
    # eva.dump_unigram_blacklist()
    # print("unigram blacklist dumped")
    
    # sent.main(run_mode)

    run_mode = configure.TRN_MODE
    sent.main(run_mode)