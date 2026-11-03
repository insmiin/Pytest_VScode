import shutil

#1.comment out files that are not needed in file_list
#2.change ETL_date
#3.change destination path if necessary
def main():
    file_list = [
        "SF_BackOfficeUser_template",
        "SF_BasketballLiveScore_template_DB1",
        "SF_BasketballLiveScore_template_DB2",
        "SF_BasketballLiveScore_template_DB3",
        "SF_BetType_template"
    ]
    ETL_date = '11110807'
    n = 0
    for fn in file_list:
        source_path = f'C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/testing/base file mssql ELT/{fn}.csv'
        new_file = fn.replace('template', ETL_date)
        destination_path = f'C:/Users/lim.miin/OneDrive - Morpheus Consulting Pte Ltd/Desktop/try ELT files/testonly/{new_file}.csv'
        shutil.copy(source_path, destination_path)
        n += 1
    print(f'Total of {n} files has been generated.')


if __name__ == "__main__":
    main()
