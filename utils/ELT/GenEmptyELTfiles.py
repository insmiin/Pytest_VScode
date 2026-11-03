import csv


def output_mem_tag(input_file, output_file):
    """
    Generates output file with '|' delimiter based on input CSV file.

    Args:
        input_file (str): Path to the input CSV file.
        output_file (str): Path to the output CSV file.
    """
    with open(input_file, 'r') as csv_file:
        with open(output_file, mode='w', newline='') as output_file:
            csv_reader = csv.DictReader(csv_file)
            csv_writer = csv.DictWriter(output_file, csv_reader.fieldnames, delimiter='|')
            csv_writer.writeheader()


def main():
    file_list = [
        "SF_User",
        "SF_EventLog",
        "SF_EventResult",
        "SF_EventResultLog",
        "SF_Event",
        "SF_Wager",
        "SF_Member",
        "SF_OddsLog",
        "SF_ReferenceEventResult"
    ]
    ETL_date = '20261006'
    n = 0
    for fn in file_list:
        input_file = f'C:/Users/lim.miin/Desktop/testing/base file ETL/{fn}_template.csv'
        #output_file = f'C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/try ELT files/20260828run(emtpy)/{fn}_{ETL_date}.csv'
        output_file = f'D:/Miin/Ghostbuster/ELT (extract load transform)/run ELT files/20261006run(empty)/{fn}_{ETL_date}.csv'
        output_mem_tag(input_file, output_file)
        n += 1
    print(f'Total of {n} files has been generated.')


if __name__ == "__main__":
    main()
