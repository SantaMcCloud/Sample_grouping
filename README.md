# fastq-groupmerge
This tool was designed to create merged samples based of a metadata file.

It is possible that a sample can be contained in multiple groups or in only one this has to be set in the metadatafile! For example here is the data from [metadata_2.csv](Test/test-data/metadata_2.csv):

```
sample_id,group
A1,control
A2,control
B1,control
B2,treatment
A1,Test_Test
B2,B2
```

It is important that the column named `sample_id` is always given in the metadata file. The column, here in the example called `group`, can be named anything since it can be set in the tool via `--group_col`.

The separator in the metadata file can also be set via the `--sep` flag but the only thing which has to be valid is that the separator set should be usable with `pandas`!

## Inputs

All of the forward and reverse FASTQ files (gzip files are supported) has to be in one directory and each of them need a valid suffix. The suffix can be anything since they can be set with the `--forward_suffix` and `--reverse_suffix`.

The metadata file is optional but recommend to use since otherwise the tool will merged all samples together into file!

## Outputs

All of the outputs are in the set `output`directory. All merged files will be gzip to save memory and the naming of the files are `{group}{(forward_suffix/reverser_suffix)}` to make them consists with the input files. If no metadata file where given the output will be one forward and one reverse file merged with all inputted files!
