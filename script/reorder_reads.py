#!/usr/bin/env python
import gzip
import shutil
import pandas as pd
from pathlib import Path
import argparse
from version import __version__


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Merge paired FASTQ (gzip possible) files based on metadata, samples can belong to multiple groups, or merge all reads together into one forward and one reverse read."
    )
    parser.add_argument(
        "--metadata",
        help="Path to metadata CSV/TSV file. If no metadata is included all files in fastq_dir will be merged to one forward and one reverse read!",
    )
    parser.add_argument("fastq_dir", help="Directory containing FASTQ files")
    parser.add_argument("output_dir", help="Output directory for merged FASTQs")
    parser.add_argument(
        "--group_col", default="group", help="Metadata column name for grouping"
    )
    parser.add_argument(
        "--sep", default=",", help="Column separator in metadata (default: ',')"
    )
    parser.add_argument(
        "--forward_suffix",
        default="_forward",
        help="Suffix to find the forward reads (default: _forward)",
    )
    parser.add_argument(
        "--reverse_suffix",
        default="_reverse",
        help="Suffix to find the reverse reads (default: _reverse)",
    )
    parser.add_argument("-v", "-V", "--version", action="version", version=__version__)
    parser.print_usage = parser.print_help

    args = parser.parse_args()

    return args


def merge_fastqs(
    metadata_file,
    fastq_dir,
    output_dir,
    group_col="group",
    sep=",",
    forward_suffix="_forward",
    reverse_suffix="_reverse",
):
    fastq_dir = Path(fastq_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    # Load metadata
    df = pd.read_csv(metadata_file, sep=sep)
    if "sample_id" not in df.columns or group_col not in df.columns:
        raise ValueError(f"Metadata must have columns: sample_id and {group_col}")

    for i, (sample_id, group) in enumerate(df.values):
        if pd.isna(sample_id) or pd.isna(group):
            print(
                f"In column {i} the followed values are set: sample_id = {sample_id} {
                    group_col
                } = {group}. Since one of both is NaN, this line will be ignored!"
            )

    df.dropna(inplace=True)

    # Each row maps one sample to one group
    groups = df.groupby(group_col)["sample_id"].apply(list).to_dict()

    for group, samples in groups.items():
        print(f"\n🔹 Merging samples for group '{group}' -> {samples}")

        out_R1 = output_dir / f"{group}_R1.fastq.gz"
        out_R2 = output_dir / f"{group}_R2.fastq.gz"

        # Remove existing output if exists
        for out_file in (out_R1, out_R2):
            if out_file.exists():
                out_file.unlink()

        # Merge each sample in this group
        for sample in samples:
            R1_gz = fastq_dir / f"{sample}{forward_suffix}.fastq.gz"
            R2_gz = fastq_dir / f"{sample}{reverse_suffix}.fastq.gz"
            R1_no_gz = fastq_dir / f"{sample}{forward_suffix}.fastq"
            R2_no_gz = fastq_dir / f"{sample}{reverse_suffix}.fastq"

            # Determine which files exist
            if R1_gz.exists() and R2_gz.exists():
                R1, R2 = R1_gz, R2_gz
            elif R1_no_gz.exists() and R2_no_gz.exists():
                R1, R2 = R1_no_gz, R2_no_gz
            else:
                print(f"⚠️  Skipping {sample}: missing one of the paired files.")
                continue

            print(f"  ➕ Adding {R1.name} and {R2.name} to group {group}")
            for src, dest in [(R1, out_R1), (R2, out_R2)]:
                open_func = gzip.open if src.suffix == ".gz" else open
                with open_func(src, "rb") as f_in, gzip.open(dest, "ab") as f_out:
                    shutil.copyfileobj(f_in, f_out)

        print(f"✅ Done: {out_R1.name}, {out_R2.name}")

    print("\n🎉 All merges complete!")


def merge_all(
    fastq_dir, output_dir, forward_suffix="_forward", reverse_suffix="_reverse"
):
    fastq_dir = Path(fastq_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    file_list = list(fastq_dir.glob("*.fastq.gz")) + list(fastq_dir.glob("*fastq"))

    if not file_list:
        print("❌ No FASTQ or FASTQ.GZ files found.")
        return

    forward_reads = sorted([f for f in file_list if f"{forward_suffix}" in f.name])
    reverse_reads = sorted([f for f in file_list if f"{reverse_suffix}" in f.name])

    print(
        f"📂 Found {len(forward_reads)} forward and {len(reverse_reads)} reverse files."
    )

    out_R1 = output_dir / f"merged{forward_suffix}.fastq.gz"
    out_R2 = output_dir / f"merged{reverse_suffix}.fastq.gz"

    for out_file in (out_R1, out_R2):
        if out_file.exists():
            out_file.unlink()

    print(f"🧬 Merging {len(forward_reads)} files into {out_R1.name}")

    for read in forward_reads:
        print(f"➕ Adding {read.name}")
        open_func = gzip.open if read.suffix == ".gz" else open
        with open_func(read, "rb") as f_in, gzip.open(out_R1, "ab") as f_out:
            shutil.copyfileobj(f_in, f_out)

    print(f"🧬 Merging {len(reverse_reads)} files into {out_R2.name}")

    for read in reverse_reads:
        print(f"➕ Adding {read.name}")
        open_func = gzip.open if read.suffix == ".gz" else open
        with open_func(read, "rb") as f_in, gzip.open(out_R2, "ab") as f_out:
            shutil.copyfileobj(f_in, f_out)

    print("\n🎉 All merges complete!")


if __name__ == "__main__":
    args = parse_arguments()

    if args.metadata:
        merge_fastqs(
            args.metadata,
            args.fastq_dir,
            args.output_dir,
            group_col=args.group_col,
            sep=args.sep,
            forward_suffix=args.forward_suffix,
            reverse_suffix=args.reverse_suffix,
        )
    else:
        merge_all(
            args.fastq_dir,
            args.output_dir,
            forward_suffix=args.forward_suffix,
            reverse_suffix=args.reverse_suffix,
        )
