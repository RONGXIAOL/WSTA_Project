import index
import eva
import sent
import sys
import configure

name_mode = {
    'dev': configure.DEV_MODE,
    'test': configure.TST_MODE,
    'train': configure.TRN_MODE,
}

if __name__ == "__main__":
    # run_mode = sys.argv[1]
    run_name = sys.argv[1]
    run_mode = name_mode[run_name]
    print(f'App run in {run_name} mode')

    index.sort_by_wiki()
    index.sort_by_corpus()
    index.dump_topics()
    index.dump_capitals()
    print("indexing done")
    
    eva.dump_unigram_blacklist()
    print("unigram blacklist dumped")
    
    sent.main(run_mode)

    eva.dump_train_set()
    print("new train set dumped for labelling model")
    