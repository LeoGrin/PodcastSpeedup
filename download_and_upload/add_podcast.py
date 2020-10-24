import argparse
import pandas as pd

def add_podcast():
    parser = argparse.ArgumentParser(description="Add a new podcast to the podcast list")
    parser.add_argument("-n", "--name", type=str, dest="full_name", nargs="+", help="Full podcast name",
                        required=True)
    parser.add_argument("-sn", "--short-name", type=str, dest="short_name", help="short name of the podcast (useful to name files)",
                        default=0)
    parser.add_argument("--original-rss",  type=str, dest="original_rss", help="RSS link of the original podcast")
    parser.add_argument("--new-rss",  type=str, dest="new_rss", help="RSS link of anchor account associated with the podcast")
    parser.add_argument("--anchor-username",  type=str, dest="anchor_username", help="Anchor login for the anchor account associated with the podcast")
    parser.add_argument("--anchor-password",  type=str, dest="anchor_password", help="Anchor password for the anchor account associated with the podcast")

    args = parser.parse_args()

    if not args.short_name:
        args.short_name = "_".join(args.full_name)
    args.full_name = " ".join(args.full_name)

    podcasts_df_file = "download_and_upload/podcasts/podcasts_db/all_podcasts_db.csv"
    podcasts_df = pd.read_csv(podcasts_df_file)
    new_row = {"full_name": args.full_name,
               "short_name": args.short_name,
               "original_rss": args.original_rss,
               "sped_up_rss": args.new_rss,
               "anchor_username": args.anchor_username,
               "anchor_password": args.anchor_password}
    podcasts_df = podcasts_df.append(new_row, ignore_index=True)
    podcasts_df.to_csv(podcasts_df_file, index=False)


if __name__ == """__main__""":
    add_podcast()

