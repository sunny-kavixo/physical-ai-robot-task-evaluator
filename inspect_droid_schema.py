"""Inspect a downloaded DROID RLDS directory before running evaluation."""
import argparse, json

def main():
    p=argparse.ArgumentParser()
    p.add_argument("dataset_dir")
    a=p.parse_args()
    import tensorflow_datasets as tfds
    b=tfds.builder_from_directory(a.dataset_dir)
    print(json.dumps({
        "name":b.info.name,
        "splits":{k:int(v.num_examples) for k,v in b.info.splits.items()},
        "features":str(b.info.features),
    },indent=2))

if __name__=="__main__":main()
